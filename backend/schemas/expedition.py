from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class ExpeditionCreate(BaseModel):
    name: str
    description: str | None = None
    region: str | None = None
    country: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: Literal["planned", "ongoing", "completed"] = "planned"
    researcher_id: int


class ExpeditionResponse(BaseModel):
    id: int
    name: str
    description: str | None
    region: str | None
    country: str | None
    start_date: datetime | None
    end_date: datetime | None
    status: str
    researcher_id: int
    created_at: datetime

    class Config:
        from_attributes = True