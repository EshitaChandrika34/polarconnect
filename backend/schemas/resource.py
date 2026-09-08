from pydantic import BaseModel
from datetime import datetime


class ResourceResponse(BaseModel):

    id: int

    title: str

    description: str | None

    resource_type: str

    file_name: str | None

    file_path: str | None

    file_size: int | None

    research_region: str | None

    keywords: str | None

    dataset_year: int | None

    dataset_version: str | None

    dataset_format: str | None

    status: str

    researcher_id: int

    created_at: datetime

    class Config:
        from_attributes = True