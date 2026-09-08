from pydantic import BaseModel

from datetime import datetime


# ============================================================
# USER CREATE
# ============================================================

class UserCreate(BaseModel):

    name: str

    email: str

    password: str


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(BaseModel):

    id: int

    name: str

    email: str

    role: str

    created_at: datetime

    class Config:

        from_attributes = True