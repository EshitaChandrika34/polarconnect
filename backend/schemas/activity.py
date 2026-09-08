from pydantic import BaseModel
from datetime import datetime


class ActivityCreate(BaseModel):
    title: str
    description: str | None = None
    activity_type: str | None = None
    location: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class ActivityResponse(BaseModel):
    id: int
    title: str
    description: str | None
    activity_type: str | None
    location: str | None
    start_date: datetime | None
    end_date: datetime | None
    researcher_id: int
    created_at: datetime

    class Config:
        from_attributes = True