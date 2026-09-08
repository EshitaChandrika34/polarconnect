from pydantic import BaseModel
from datetime import datetime


class VideoCreate(BaseModel):
    title: str
    description: str | None = None
    video_path: str
    location: str | None = None
    duration: str | None = None
    researcher_id: int


class VideoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    video_path: str
    location: str | None
    duration: str | None
    researcher_id: int
    created_at: datetime

    class Config:
        from_attributes = True