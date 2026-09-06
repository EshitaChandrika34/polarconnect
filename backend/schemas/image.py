from pydantic import BaseModel
from datetime import datetime


class ImageCreate(BaseModel):
    title: str
    description: str | None = None
    image_path: str
    location: str | None = None
    captured_date: str | None = None
    researcher_id: int


class ImageResponse(BaseModel):
    id: int
    title: str
    description: str | None
    image_path: str
    location: str | None
    captured_date: str | None
    researcher_id: int
    created_at: datetime

    class Config:
        from_attributes = True