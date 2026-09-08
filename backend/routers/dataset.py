from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from io import BytesIO
import uuid

from database import get_db
from models.dataset import Dataset
from schemas.dataset import DatasetResponse

from storage.minio_client import client, MINIO_BUCKET

from auth import get_current_user


router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"]
)


# ============================================================
# 1. UPLOAD DATASET
# ============================================================

@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    title: str = Form(...),
    description: str = Form(None),
    dataset_type: str = Form(None),
    location: str = Form(None),
    file: UploadFile = File(...),

    current_user=Depends(get_current_user),

    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="File is required"
        )

    # --------------------------------------------------------
    # Get file extension
    # --------------------------------------------------------

    extension = ""

    if "." in file.filename:

        extension = "." + file.filename.split(".")[-1]

    # --------------------------------------------------------
    # Create unique MinIO object name
    # --------------------------------------------------------

    object_name = (
        f"datasets/"
        f"{uuid.uuid4()}"
        f"{extension}"
    )

    # --------------------------------------------------------
    # Read uploaded file
    # --------------------------------------------------------

    file_content = await file.read()

    file_size = len(file_content)

    # --------------------------------------------------------
    # Upload file to MinIO
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
    # Save metadata in PostgreSQL
    # --------------------------------------------------------

    dataset = Dataset(
        title=title,
        description=description,
        dataset_type=dataset_type,
        location=location,

        # MinIO path
        file_path=object_name,

        # Automatically use logged-in user
        researcher_id=current_user.id
    )

    try:

        db.add(dataset)

        db.commit()

        db.refresh(dataset)

    except Exception as e:

        db.rollback()

        # Remove MinIO file if database save fails
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

    return dataset


# ============================================================
# 2. GET ALL DATASETS
# ============================================================

@router.get(
    "/",
    response_model=list[DatasetResponse]
)
def get_datasets(
    db: Session = Depends(get_db)
):

    datasets = (
        db.query(Dataset)
        .order_by(
            Dataset.created_at.desc()
        )
        .all()
    )

    return datasets


# ============================================================
# 3. GET DATASET BY ID
# ============================================================

@router.get(
    "/{dataset_id}",
    response_model=DatasetResponse
)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
):

    dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == dataset_id
        )
        .first()
    )

    if not dataset:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    return dataset


# ============================================================
# 4. DOWNLOAD DATASET
# ============================================================

@router.get(
    "/{dataset_id}/download"
)
def download_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
):

    dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == dataset_id
        )
        .first()
    )

    if not dataset:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    if not dataset.file_path:

        raise HTTPException(
            status_code=404,
            detail="Dataset file not found"
        )

    try:

        response = client.get_object(
            MINIO_BUCKET,
            dataset.file_path
        )

        file_data = response.read()

        response.close()
        response.release_conn()

        # Try to preserve a useful filename
        filename = dataset.title

        return StreamingResponse(
            BytesIO(file_data),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition":
                f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"File download failed: {str(e)}"
        )


# ============================================================
# 5. UPDATE DATASET
# ============================================================

@router.put(
    "/{dataset_id}",
    response_model=DatasetResponse
)
def update_dataset(
    dataset_id: int,

    title: str = Form(...),
    description: str = Form(None),
    dataset_type: str = Form(None),
    location: str = Form(None),

    current_user=Depends(get_current_user),

    db: Session = Depends(get_db)
):

    dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == dataset_id
        )
        .first()
    )

    if not dataset:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # --------------------------------------------------------
    # Only the researcher who uploaded it can update it
    # --------------------------------------------------------

    if dataset.researcher_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="You can only update your own dataset"
        )

    # --------------------------------------------------------
    # Update metadata
    # --------------------------------------------------------

    dataset.title = title
    dataset.description = description
    dataset.dataset_type = dataset_type
    dataset.location = location

    db.commit()

    db.refresh(dataset)

    return dataset


# ============================================================
# 6. DELETE DATASET
# ============================================================

@router.delete(
    "/{dataset_id}"
)
def delete_dataset(
    dataset_id: int,

    current_user=Depends(get_current_user),

    db: Session = Depends(get_db)
):

    dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == dataset_id
        )
        .first()
    )

    if not dataset:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # --------------------------------------------------------
    # Only owner can delete dataset
    # --------------------------------------------------------

    if dataset.researcher_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="You can only delete your own dataset"
        )

    # --------------------------------------------------------
    # Delete actual file from MinIO
    # --------------------------------------------------------

    if dataset.file_path:

        try:

            client.remove_object(
                MINIO_BUCKET,
                dataset.file_path
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=f"MinIO delete failed: {str(e)}"
            )

    # --------------------------------------------------------
    # Delete metadata from PostgreSQL
    # --------------------------------------------------------

    db.delete(dataset)

    db.commit()

    return {
        "message": "Dataset deleted successfully",
        "dataset_id": dataset_id
    }