from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.expedition import Expedition
from models.user import User
from schemas.expedition import ExpeditionCreate, ExpeditionResponse
from auth import get_current_user


router = APIRouter(
    prefix="/expeditions",
    tags=["Expeditions"]
)


# =========================================================
# CREATE EXPEDITION
# POST /expeditions/
# =========================================================

@router.post("/", response_model=ExpeditionResponse)
def create_expedition(
    expedition: ExpeditionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    new_expedition = Expedition(
        name=expedition.name,
        description=expedition.description,
        region=expedition.region,
        country=expedition.country,
        start_date=expedition.start_date,
        end_date=expedition.end_date,
        status=expedition.status,
        researcher_id=current_user.id
    )

    try:
        db.add(new_expedition)
        db.commit()
        db.refresh(new_expedition)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create expedition: {str(e)}"
        )

    return new_expedition


# =========================================================
# GET ALL EXPEDITIONS
# GET /expeditions/
# =========================================================

@router.get("/", response_model=list[ExpeditionResponse])
def get_expeditions(
    db: Session = Depends(get_db)
):

    expeditions = (
        db.query(Expedition)
        .order_by(Expedition.start_date.desc())
        .all()
    )

    return expeditions


# =========================================================
# GET MY EXPEDITIONS
# GET /expeditions/my
# =========================================================

@router.get("/my", response_model=list[ExpeditionResponse])
def get_my_expeditions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    expeditions = (
        db.query(Expedition)
        .filter(Expedition.researcher_id == current_user.id)
        .order_by(Expedition.start_date.desc())
        .all()
    )

    return expeditions


# =========================================================
# GET EXPEDITION BY ID
# GET /expeditions/{expedition_id}
# =========================================================

@router.get("/{expedition_id}", response_model=ExpeditionResponse)
def get_expedition(
    expedition_id: int,
    db: Session = Depends(get_db)
):

    expedition = (
        db.query(Expedition)
        .filter(Expedition.id == expedition_id)
        .first()
    )

    if not expedition:
        raise HTTPException(
            status_code=404,
            detail="Expedition not found"
        )

    return expedition


# =========================================================
# UPDATE EXPEDITION
# PUT /expeditions/{expedition_id}
# =========================================================

@router.put("/{expedition_id}", response_model=ExpeditionResponse)
def update_expedition(
    expedition_id: int,
    expedition_data: ExpeditionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    expedition = (
        db.query(Expedition)
        .filter(Expedition.id == expedition_id)
        .first()
    )

    if not expedition:
        raise HTTPException(
            status_code=404,
            detail="Expedition not found"
        )

    if expedition.researcher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own expedition"
        )

    expedition.name = expedition_data.name
    expedition.description = expedition_data.description
    expedition.region = expedition_data.region
    expedition.country = expedition_data.country
    expedition.start_date = expedition_data.start_date
    expedition.end_date = expedition_data.end_date
    expedition.status = expedition_data.status

    try:
        db.commit()
        db.refresh(expedition)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update expedition: {str(e)}"
        )

    return expedition


# =========================================================
# DELETE EXPEDITION
# DELETE /expeditions/{expedition_id}
# =========================================================

@router.delete("/{expedition_id}")
def delete_expedition(
    expedition_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    expedition = (
        db.query(Expedition)
        .filter(Expedition.id == expedition_id)
        .first()
    )

    if not expedition:
        raise HTTPException(
            status_code=404,
            detail="Expedition not found"
        )

    if expedition.researcher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own expedition"
        )

    try:
        db.delete(expedition)
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete expedition: {str(e)}"
        )

    return {
        "message": "Expedition deleted successfully",
        "expedition_id": expedition_id
    }