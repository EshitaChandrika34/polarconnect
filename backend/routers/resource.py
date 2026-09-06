import os
import uuid
from io import BytesIO

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from models.resource import Resource
from models.user import User
from storage.minio_client import client, MINIO_BUCKET
from schemas.resource import ResourceResponse
from auth import get_current_user


# ============================================================
# FILE VALIDATION SETTINGS
# ============================================================

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

ALLOWED_EXTENSIONS = {
    "report": {
        ".pdf",
        ".doc",
        ".docx"
    },
    "publication": {
        ".pdf",
        ".doc",
        ".docx"
    },
    "dataset": {
        ".csv",
        ".xlsx",
        ".xls",
        ".json",
        ".zip"
    },
    "image": {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    },
    "video": {
        ".mp4",
        ".mov",
        ".avi",
        ".webm"
    }
}


router = APIRouter(
    prefix="/resources",
    tags=["Resources"]
)


# ============================================================
# 1. UPLOAD RESOURCE
# ============================================================

@router.post(
    "/upload",
    response_model=ResourceResponse
)
async def upload_resource(
    title: str = Form(...),
    description: str = Form(None),
    resource_type: str = Form(...),
    research_region: str = Form(None),
    keywords: str = Form(None),

    # Dataset-specific fields
    dataset_year: int = Form(None),
    dataset_version: str = Form(None),
    dataset_format: str = Form(None),

    file: UploadFile = File(...),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # ALLOWED RESOURCE TYPES
    # --------------------------------------------------------

    allowed_types = [
        "report",
        "publication",
        "dataset",
        "image",
        "video"
    ]

    resource_type = resource_type.lower().strip()

    if resource_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid resource type"
        )

    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File is required"
        )

    # --------------------------------------------------------
    # CHECK FILE EXTENSION
    # --------------------------------------------------------

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    allowed_extensions = ALLOWED_EXTENSIONS.get(
        resource_type,
        set()
    )

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File type '{extension}' is not allowed "
                f"for {resource_type}"
            )
        )

    # --------------------------------------------------------
    # READ FILE
    # --------------------------------------------------------

    file_content = await file.read()

    file_size = len(file_content)

    # Empty file check
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    # Maximum size check
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the 50 MB limit"
        )

    # --------------------------------------------------------
    # GENERATE UNIQUE MINIO OBJECT NAME
    # --------------------------------------------------------

    object_name = (
        f"{resource_type}/"
        f"{uuid.uuid4()}"
        f"{extension}"
    )

    # --------------------------------------------------------
    # UPLOAD FILE TO MINIO
    # --------------------------------------------------------

    try:

        client.put_object(
            MINIO_BUCKET,
            object_name,
            BytesIO(file_content),
            length=file_size,
            content_type=(
                file.content_type
                or "application/octet-stream"
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"MinIO upload failed: {str(e)}"
        )

    # --------------------------------------------------------
    # SAVE METADATA TO POSTGRESQL
    # --------------------------------------------------------

    resource = Resource(
        title=title,
        description=description,
        resource_type=resource_type,

        file_name=file.filename,
        file_path=object_name,
        file_size=file_size,

        research_region=research_region,
        keywords=keywords,

        dataset_year=dataset_year,
        dataset_version=dataset_version,
        dataset_format=dataset_format,

        # New resources require admin approval
        status="pending",

        # Logged-in user's ID
        researcher_id=current_user.id
    )

    try:

        db.add(resource)
        db.commit()
        db.refresh(resource)

    except Exception as e:

        db.rollback()

        # If database fails, remove uploaded MinIO file
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

    return resource


# ============================================================
# 2. GET ALL APPROVED RESOURCES
# ============================================================

@router.get(
    "/",
    response_model=list[ResourceResponse]
)
def get_resources(
    db: Session = Depends(get_db)
):

    resources = (
        db.query(Resource)
        .filter(
            Resource.status == "approved"
        )
        .order_by(
            Resource.created_at.desc()
        )
        .all()
    )

    return resources


# ============================================================
# 3. SEARCH / FILTER RESOURCES
# ============================================================

@router.get(
    "/search",
    response_model=list[ResourceResponse]
)
def search_resources(
    title: str | None = None,
    resource_type: str | None = None,
    research_region: str | None = None,
    keywords: str | None = None,
    db: Session = Depends(get_db)
):

    query = (
        db.query(Resource)
        .filter(
            Resource.status == "approved"
        )
    )

    if title:
        query = query.filter(
            Resource.title.ilike(
                f"%{title}%"
            )
        )

    if resource_type:
        query = query.filter(
            Resource.resource_type.ilike(
                f"%{resource_type}%"
            )
        )

    if research_region:
        query = query.filter(
            Resource.research_region.ilike(
                f"%{research_region}%"
            )
        )

    if keywords:
        query = query.filter(
            Resource.keywords.ilike(
                f"%{keywords}%"
            )
        )

    return (
        query
        .order_by(
            Resource.created_at.desc()
        )
        .all()
    )


# ============================================================
# 4. GET MY RESOURCES
# ============================================================

@router.get(
    "/my",
    response_model=list[ResourceResponse]
)
def get_my_resources(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    resources = (
        db.query(Resource)
        .filter(
            Resource.researcher_id
            == current_user.id
        )
        .order_by(
            Resource.created_at.desc()
        )
        .all()
    )

    return resources


# ============================================================
# 5. UPDATE RESOURCE
# ============================================================

@router.put(
    "/{resource_id}",
    response_model=ResourceResponse
)
def update_resource(
    resource_id: int,

    title: str = Form(...),
    description: str = Form(None),
    resource_type: str = Form(...),
    research_region: str = Form(None),
    keywords: str = Form(None),

    dataset_year: int = Form(None),
    dataset_version: str = Form(None),
    dataset_format: str = Form(None),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    resource = (
        db.query(Resource)
        .filter(
            Resource.id == resource_id
        )
        .first()
    )

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    # --------------------------------------------------------
    # ONLY OWNER CAN UPDATE
    # --------------------------------------------------------

    if resource.researcher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail=(
                "You can only update "
                "your own resource"
            )
        )

    # --------------------------------------------------------
    # VALIDATE RESOURCE TYPE
    # --------------------------------------------------------

    resource_type = resource_type.lower().strip()

    if resource_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid resource type"
        )

    # --------------------------------------------------------
    # UPDATE DATA
    # --------------------------------------------------------

    resource.title = title
    resource.description = description
    resource.resource_type = resource_type
    resource.research_region = research_region
    resource.keywords = keywords

    resource.dataset_year = dataset_year
    resource.dataset_version = dataset_version
    resource.dataset_format = dataset_format

    # Updated resource requires approval again
    resource.status = "pending"

    try:

        db.commit()
        db.refresh(resource)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to update resource: {str(e)}"
            )
        )

    return resource


# ============================================================
# 6. DELETE RESOURCE
# ============================================================

@router.delete(
    "/{resource_id}"
)
def delete_resource(
    resource_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    resource = (
        db.query(Resource)
        .filter(
            Resource.id == resource_id
        )
        .first()
    )

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    # --------------------------------------------------------
    # ONLY OWNER CAN DELETE
    # --------------------------------------------------------

    if resource.researcher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail=(
                "You can only delete "
                "your own resource"
            )
        )

    # --------------------------------------------------------
    # DELETE FILE FROM MINIO
    # --------------------------------------------------------

    if resource.file_path:

        try:

            client.remove_object(
                MINIO_BUCKET,
                resource.file_path
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=(
                    f"MinIO delete failed: {str(e)}"
                )
            )

    # --------------------------------------------------------
    # DELETE DATABASE RECORD
    # --------------------------------------------------------

    try:

        db.delete(resource)
        db.commit()

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to delete resource: {str(e)}"
            )
        )

    return {
        "message": "Resource deleted successfully",
        "resource_id": resource_id
    }


# ============================================================
# 7. DOWNLOAD RESOURCE
# ============================================================
# IMPORTANT:
# This route is BEFORE /{resource_id}
# ============================================================

@router.get(
    "/{resource_id}/download"
)
def download_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):

    resource = (
        db.query(Resource)
        .filter(
            Resource.id == resource_id
        )
        .first()
    )

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    if not resource.file_path:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    # --------------------------------------------------------
    # ONLY APPROVED RESOURCES CAN BE DOWNLOADED
    # --------------------------------------------------------

    if resource.status != "approved":
        raise HTTPException(
            status_code=403,
            detail="Resource is not approved yet"
        )

    # --------------------------------------------------------
    # DOWNLOAD FROM MINIO
    # --------------------------------------------------------

    try:

        response = client.get_object(
            MINIO_BUCKET,
            resource.file_path
        )

        file_data = response.read()

        response.close()
        response.release_conn()

        return StreamingResponse(
            BytesIO(file_data),

            media_type=(
                "application/octet-stream"
            ),

            headers={
                "Content-Disposition":
                (
                    f'attachment; '
                    f'filename="{resource.file_name}"'
                )
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"File download failed: {str(e)}"
            )
        )


# ============================================================
# 8. GET RESOURCE BY ID
# ============================================================

@router.get(
    "/{resource_id}",
    response_model=ResourceResponse
)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):

    resource = (
        db.query(Resource)
        .filter(
            Resource.id == resource_id
        )
        .first()
    )

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    return resource