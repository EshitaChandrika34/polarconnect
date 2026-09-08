from pydantic import BaseModel
from datetime import datetime


# =========================================================
# CREATE PUBLICATION
# =========================================================

class PublicationCreate(BaseModel):
    title: str
    authors: str | None = None
    abstract: str | None = None
    journal: str | None = None
    publication_year: int | None = None
    doi: str | None = None
    file_path: str | None = None


# =========================================================
# PUBLICATION RESPONSE
# =========================================================

class PublicationResponse(BaseModel):
    id: int
    title: str
    authors: str | None
    abstract: str | None
    journal: str | None
    publication_year: int | None
    doi: str | None
    file_path: str | None
    researcher_id: int
    created_at: datetime

    class Config:
        from_attributes = True