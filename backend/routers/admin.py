from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.resource import Resource
from auth import get_current_admin
from models.user import User
from models.dataset import Dataset
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# ============================================================
# GET PENDING RESOURCES
# ============================================================

@router.get("/resources/pending")
def get_pending_resources(
    db: Session = Depends(get_db)
):
    resources = (
        db.query(Resource)
        .filter(Resource.status == "pending")
        .order_by(Resource.created_at.desc())
        .all()
    )

    return resources


# ============================================================
# APPROVE RESOURCE
# ============================================================

@router.put("/resources/{resource_id}/approve")
def approve_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    resource = (
        db.query(Resource)
        .filter(Resource.id == resource_id)
        .first()
    )

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    if resource.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Resource is already {resource.status}"
        )

    resource.status = "approved"

    db.commit()
    db.refresh(resource)

    return {
        "message": "Resource approved successfully",
        "resource_id": resource.id,
        "status": resource.status
    }


# ============================================================
# REJECT RESOURCE
# ============================================================

@router.put("/resources/{resource_id}/reject")
def reject_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    resource = (
        db.query(Resource)
        .filter(Resource.id == resource_id)
        .first()
    )

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    if resource.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Resource is already {resource.status}"
        )

    resource.status = "rejected"

    db.commit()
    db.refresh(resource)

    return {
        "message": "Resource rejected successfully",
        "resource_id": resource.id,
        "status": resource.status
    }
# ============================================================
# DATASET ADMIN MANAGEMENT
# ============================================================

@router.get("/datasets/pending")
def get_pending_datasets(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    datasets = (
        db.query(Dataset)
        .filter(Dataset.status == "pending")
        .order_by(Dataset.created_at.desc())
        .all()
    )

    return datasets


@router.put("/datasets/{dataset_id}/approve")
def approve_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id)
        .first()
    )

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    if dataset.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Dataset is already {dataset.status}"
        )

    dataset.status = "approved"

    db.commit()
    db.refresh(dataset)

    return {
        "message": "Dataset approved successfully",
        "dataset_id": dataset.id,
        "status": dataset.status
    }


@router.put("/datasets/{dataset_id}/reject")
def reject_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id)
        .first()
    )

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    if dataset.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Dataset is already {dataset.status}"
        )

    dataset.status = "rejected"

    db.commit()
    db.refresh(dataset)

    return {
        "message": "Dataset rejected successfully",
        "dataset_id": dataset.id,
        "status": dataset.status
    }

# ============================================================
# ADMIN DASHBOARD STATISTICS
# ============================================================

@router.get("/dashboard")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    total_users = db.query(User).count()

    total_resources = db.query(Resource).count()
    pending_resources = (
        db.query(Resource)
        .filter(Resource.status == "pending")
        .count()
    )
    approved_resources = (
        db.query(Resource)
        .filter(Resource.status == "approved")
        .count()
    )
    rejected_resources = (
        db.query(Resource)
        .filter(Resource.status == "rejected")
        .count()
    )

    total_datasets = db.query(Dataset).count()
    pending_datasets = (
        db.query(Dataset)
        .filter(Dataset.status == "pending")
        .count()
    )
    approved_datasets = (
        db.query(Dataset)
        .filter(Dataset.status == "approved")
        .count()
    )
    rejected_datasets = (
        db.query(Dataset)
        .filter(Dataset.status == "rejected")
        .count()
    )

    return {
        "users": {
            "total": total_users
        },

        "resources": {
            "total": total_resources,
            "pending": pending_resources,
            "approved": approved_resources,
            "rejected": rejected_resources
        },

        "datasets": {
            "total": total_datasets,
            "pending": pending_datasets,
            "approved": approved_datasets,
            "rejected": rejected_datasets
        }
    }