from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.activity import Activity
from models.user import User
from auth import get_current_user
from schemas.activity import ActivityCreate, ActivityResponse


router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


# =========================================================
# CREATE ACTIVITY
# POST /activities/
# =========================================================

@router.post("/", response_model=ActivityResponse)
def create_activity(
    activity: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    new_activity = Activity(
        title=activity.title,
        description=activity.description,
        activity_type=activity.activity_type,
        location=activity.location,
        start_date=activity.start_date,
        end_date=activity.end_date,
        researcher_id=current_user.id
    )

    try:
        db.add(new_activity)
        db.commit()
        db.refresh(new_activity)

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create activity: {str(e)}"
        )

    return new_activity


# =========================================================
# GET ALL ACTIVITIES
# GET /activities/
# =========================================================

@router.get("/", response_model=list[ActivityResponse])
def get_activities(
    db: Session = Depends(get_db)
):

    activities = (
        db.query(Activity)
        .order_by(Activity.start_date.desc())
        .all()
    )

    return activities


# =========================================================
# GET MY ACTIVITIES
# GET /activities/my
# =========================================================

@router.get("/my", response_model=list[ActivityResponse])
def get_my_activities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    activities = (
        db.query(Activity)
        .filter(Activity.researcher_id == current_user.id)
        .order_by(Activity.start_date.desc())
        .all()
    )

    return activities


# =========================================================
# GET ACTIVITY BY ID
# GET /activities/{activity_id}
# =========================================================

@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db)
):

    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id)
        .first()
    )

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    return activity


# =========================================================
# UPDATE ACTIVITY
# PUT /activities/{activity_id}
# =========================================================

@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    activity_data: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id)
        .first()
    )

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    # Only owner can update
    if activity.researcher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own activity"
        )

    activity.title = activity_data.title
    activity.description = activity_data.description
    activity.activity_type = activity_data.activity_type
    activity.location = activity_data.location
    activity.start_date = activity_data.start_date
    activity.end_date = activity_data.end_date

    try:
        db.commit()
        db.refresh(activity)

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to update activity: {str(e)}"
        )

    return activity


# =========================================================
# DELETE ACTIVITY
# DELETE /activities/{activity_id}
# =========================================================

@router.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id)
        .first()
    )

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    # Only owner can delete
    if activity.researcher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own activity"
        )

    try:
        db.delete(activity)
        db.commit()

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete activity: {str(e)}"
        )

    return {
        "message": "Activity deleted successfully",
        "activity_id": activity_id
    }