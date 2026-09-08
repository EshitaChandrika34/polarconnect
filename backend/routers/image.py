import os
import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from models.image import Image
from models.user import User
from auth import get_current_user
from storage.minio_client import client, MINIO_BUCKET


# =========================================================
# SETTINGS
# =========================================================

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


router = APIRouter(
    prefix="/images",
    tags=["Images"]
)


# =========================================================
# UPLOAD IMAGE
# POST /images/upload
# =========================================================

@router.post("/upload")
async def upload_image(
    title: str = Form(...),
    description: str = Form(None),
    location: str = Form(None),
    captured_date: str = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Check filename
    # -----------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Image file is required"
        )

    # -----------------------------------------------------
    # Check extension
    # -----------------------------------------------------

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed"
        )

    # -----------------------------------------------------
    # Read file
    # -----------------------------------------------------

    file_content = await file.read()

    file_size = len(file_content)

    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty"
        )

    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size exceeds the 10 MB limit"
        )

    # -----------------------------------------------------
    # Create unique MinIO object name
    # -----------------------------------------------------

    object_name = f"images/{uuid.uuid4()}{extension}"

    # -----------------------------------------------------
    # Upload to MinIO
    # -----------------------------------------------------

    try:

        client.put_object(
            MINIO_BUCKET,
            object_name,
            BytesIO(file_content),
            length=file_size,
            content_type=file.content_type or "application/octet-stream"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"MinIO image upload failed: {str(e)}"
        )

    # -----------------------------------------------------
    # Save image metadata in PostgreSQL
    # -----------------------------------------------------

    new_image = Image(
        title=title,
        description=description,
        image_path=object_name,
        location=location,
        captured_date=captured_date,
        researcher_id=current_user.id
    )

    try:

        db.add(new_image)
        db.commit()
        db.refresh(new_image)

    except Exception as e:

        db.rollback()

        # Remove MinIO file if database insertion fails
        try:
            client.remove_object(
                MINIO_BUCKET,
                object_name
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    return {
        "message": "Image uploaded successfully",
        "image_id": new_image.id,
        "title": new_image.title,
        "image_path": new_image.image_path,
        "location": new_image.location,
        "captured_date": new_image.captured_date,
        "researcher_id": new_image.researcher_id
    }


# =========================================================
# GET ALL IMAGES
# GET /images/
# =========================================================

@router.get("/")
def get_images(
    db: Session = Depends(get_db)
):

    images = (
        db.query(Image)
        .order_by(Image.created_at.desc())
        .all()
    )

    return images


# =========================================================
# GET MY IMAGES
# GET /images/my
# =========================================================

@router.get("/my")
def get_my_images(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    images = (
        db.query(Image)
        .filter(Image.researcher_id == current_user.id)
        .order_by(Image.created_at.desc())
        .all()
    )

    return images


# =========================================================
# DOWNLOAD IMAGE
# GET /images/{image_id}/download
# =========================================================

@router.get("/{image_id}/download")
def download_image(
    image_id: int,
    db: Session = Depends(get_db)
):

    image = (
        db.query(Image)
        .filter(Image.id == image_id)
        .first()
    )

    if not image:
        raise HTTPException(
            status_code=404,
            detail="Image not found"
        )

    if not image.image_path:
        raise HTTPException(
            status_code=404,
            detail="Image file not found"
        )

    try:

        response = client.get_object(
            MINIO_BUCKET,
            image.image_path
        )

        file_data = response.read()

        response.close()
        response.release_conn()

        extension = os.path.splitext(image.image_path)[1].lower()

        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp"
        }

        media_type = media_types.get(
            extension,
            "application/octet-stream"
        )

        return StreamingResponse(
            BytesIO(file_data),
            media_type=media_type,
            headers={
                "Content-Disposition":
                    f'attachment; filename="{image.title}{extension}"'
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Image download failed: {str(e)}"
        )


# =========================================================
# GET IMAGE BY ID
# GET /images/{image_id}
# =========================================================

@router.get("/{image_id}")
def get_image(
    image_id: int,
    db: Session = Depends(get_db)
):

    image = (
        db.query(Image)
        .filter(Image.id == image_id)
        .first()
    )

    if not image:
        raise HTTPException(
            status_code=404,
            detail="Image not found"
        )

    return image


# =========================================================
# DELETE IMAGE
# DELETE /images/{image_id}
# =========================================================

@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    image = (
        db.query(Image)
        .filter(Image.id == image_id)
        .first()
    )

    if not image:
        raise HTTPException(
            status_code=404,
            detail="Image not found"
        )

    # -----------------------------------------------------
    # Only owner can delete
    # -----------------------------------------------------

    if image.researcher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own image"
        )

    # -----------------------------------------------------
    # Delete from MinIO
    # -----------------------------------------------------

    if image.image_path:

        try:

            client.remove_object(
                MINIO_BUCKET,
                image.image_path
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=f"MinIO image delete failed: {str(e)}"
            )

    # -----------------------------------------------------
    # Delete database record
    # -----------------------------------------------------

    try:

        db.delete(image)
        db.commit()

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete image: {str(e)}"
        )

    return {
        "message": "Image deleted successfully",
        "image_id": image_id
    }