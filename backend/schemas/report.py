from pydantic import BaseModel
from datetime import datetime


# =========================================================
# CREATE REPORT
# =========================================================

class ReportCreate(BaseModel):
    title: str
    description: str | None = None
    file_path: str | None = None


# =========================================================
# REPORT RESPONSE
# =========================================================

class ReportResponse(BaseModel):
    id: int
    title: str
    description: str | None
    file_path: str | None
    status: str
    researcher_id: int
    created_at: datetime

    class Config:
        from_attributes = True