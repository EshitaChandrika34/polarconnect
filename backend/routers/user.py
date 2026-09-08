from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database import get_db
from models.user import User

from schemas.user import (
    UserCreate,
    UserResponse
)

from auth import (
    hash_password,
    get_current_user
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ============================================================
# GET ALL USERS
# ============================================================

@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db)
):

    users = (
        db.query(User)
        .order_by(User.id)
        .all()
    )

    return users


# ============================================================
# CREATE NEW ACCOUNT
# ============================================================

@router.post(
    "/",
    response_model=UserResponse
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # Check if email already exists

    existing_user = (
        db.query(User)
        .filter(
            User.email == user.email
        )
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password

    hashed_password = hash_password(
        user.password
    )

    # New users are PUBLIC by default

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role="PUBLIC"
    )

    try:

        db.add(new_user)

        db.commit()

        db.refresh(new_user)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to create user"
        )

    return new_user


# ============================================================
# GET MY PROFILE
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(
        get_current_user
    )
):

    return current_user


# ============================================================
# GET USER BY ID
# ============================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# ============================================================
# UPDATE USER
# ============================================================

@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    user_data: UserCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # --------------------------------------------------------
    # User can update only their own account
    # --------------------------------------------------------

    if current_user.id != user_id:

        raise HTTPException(
            status_code=403,
            detail="You can only update your own account"
        )

    # --------------------------------------------------------
    # Check email
    # --------------------------------------------------------

    existing_user = (
        db.query(User)
        .filter(
            User.email == user_data.email,
            User.id != user_id
        )
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # --------------------------------------------------------
    # Update details
    # --------------------------------------------------------

    user.name = user_data.name

    user.email = user_data.email

    user.password = hash_password(
        user_data.password
    )

    # --------------------------------------------------------
    # Save changes
    # --------------------------------------------------------

    try:

        db.commit()

        db.refresh(user)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to update user"
        )

    return user


# ============================================================
# DELETE USER
# ============================================================

@router.delete(
    "/{user_id}"
)
def delete_user(
    user_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # --------------------------------------------------------
    # User can delete only their own account
    # --------------------------------------------------------

    if current_user.id != user_id:

        raise HTTPException(
            status_code=403,
            detail="You can only delete your own account"
        )

    # --------------------------------------------------------
    # Delete user
    # --------------------------------------------------------

    try:

        db.delete(user)

        db.commit()

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to delete user"
        )

    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }