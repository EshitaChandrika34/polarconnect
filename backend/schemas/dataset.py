from pydantic import BaseModel
from datetime import datetime


class DatasetCreate(BaseModel):
    title: str
    description: str | None = None
    dataset_type: str | None = None
    location: str | None = None
    file_path: str | None = None
    researcher_id: int


class DatasetResponse(BaseModel):
    id: int
    title: str
    description: str | None
    dataset_type: str | None
    location: str | None
    file_path: str | None
    status: str
    researcher_id: int
    created_at: datetime

    class Config:
        from_attributes = True