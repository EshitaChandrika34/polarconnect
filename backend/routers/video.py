import os
import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from models.video import Video
from models.user import User
from auth import get_current_user
from storage.minio_client import client, MINIO_BUCKET


MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB

ALLOWED_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".webm"
}


router = APIRouter(
    prefix="/videos",
    tags=["Videos"]
)


# =========================================================
# UPLOAD VIDEO
# POST /videos/upload
# =========================================================

@router.post("/upload")
async def upload_video(
    title: str = Form(...),
    description: str = Form(None),
    location: str = Form(None),
    duration: str = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Video file is required"
        )

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only MP4, MOV, AVI and WEBM videos are allowed"
        )

    file_content = await file.read()
    file_size = len(file_content)

    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded video is empty"
        )

    if file_size > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Video size exceeds the 100 MB limit"
        )

    object_name = f"videos/{uuid.uuid4()}{extension}"

    # Upload actual video to MinIO
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
            detail=f"MinIO video upload failed: {str(e)}"
        )

    # Store metadata in PostgreSQL
    new_video = Video(
        title=title,
        description=description,
        video_path=object_name,
        location=location,
        duration=duration,
        researcher_id=current_user.id
    )

    try:
        db.add(new_video)
        db.commit()
        db.refresh(new_video)

    except Exception as e:
        db.rollback()

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
        "message": "Video uploaded successfully",
        "video_id": new_video.id,
        "title": new_video.title,
        "video_path": new_video.video_path,
        "location": new_video.location,
        "duration": new_video.duration,
        "researcher_id": new_video.researcher_id
    }


# =========================================================
# GET ALL VIDEOS
# GET /videos/
# =========================================================

@router.get("/")
def get_videos(
    db: Session = Depends(get_db)
):

    videos = (
        db.query(Video)
        .order_by(Video.created_at.desc())
        .all()
    )

    return videos


# =========================================================
# GET MY VIDEOS
# GET /videos/my
# =========================================================

@router.get("/my")
def get_my_videos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    videos = (
        db.query(Video)
        .filter(Video.researcher_id == current_user.id)
        .order_by(Video.created_at.desc())
        .all()
    )

    return videos


# =========================================================
# DOWNLOAD VIDEO
# IMPORTANT: Keep this BEFORE /{video_id}
# =========================================================

@router.get("/{video_id}/download")
def download_video(
    video_id: int,
    db: Session = Depends(get_db)
):

    video = (
        db.query(Video)
        .filter(Video.id == video_id)
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=404,
            detail="Video not found"
        )

    if not video.video_path:
        raise HTTPException(
            status_code=404,
            detail="Video file not found"
        )

    try:

        response = client.get_object(
            MINIO_BUCKET,
            video.video_path
        )

        file_data = response.read()

        response.close()
        response.release_conn()

        extension = os.path.splitext(
            video.video_path
        )[1].lower()

        media_types = {
            ".mp4": "video/mp4",
            ".mov": "video/quicktime",
            ".avi": "video/x-msvideo",
            ".webm": "video/webm"
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
                    f'attachment; filename="{video.title}{extension}"'
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Video download failed: {str(e)}"
        )


# =========================================================
# GET VIDEO BY ID
# GET /videos/{video_id}
# =========================================================

@router.get("/{video_id}")
def get_video(
    video_id: int,
    db: Session = Depends(get_db)
):

    video = (
        db.query(Video)
        .filter(Video.id == video_id)
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=404,
            detail="Video not found"
        )

    return video


# =========================================================
# DELETE VIDEO
# DELETE /videos/{video_id}
# =========================================================

@router.delete("/{video_id}")
def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    video = (
        db.query(Video)
        .filter(Video.id == video_id)
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=404,
            detail="Video not found"
        )

    if video.researcher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own video"
        )

    # Delete actual video from MinIO
    if video.video_path:

        try:
            client.remove_object(
                MINIO_BUCKET,
                video.video_path
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"MinIO video delete failed: {str(e)}"
            )

    # Delete metadata from PostgreSQL
    try:
        db.delete(video)
        db.commit()

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete video: {str(e)}"
        )

    return {
        "message": "Video deleted successfully",
        "video_id": video_id
    }