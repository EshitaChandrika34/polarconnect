from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)

    description = Column(Text, nullable=True)

    resource_type = Column(String(50), nullable=False)

    file_name = Column(String(255), nullable=True)

    file_path = Column(String(500), nullable=True)

    file_size = Column(Integer, nullable=True)

    research_region = Column(String(255), nullable=True)

    keywords = Column(String(500), nullable=True)

    # Dataset-specific metadata
    dataset_year = Column(Integer, nullable=True)

    dataset_version = Column(String(50), nullable=True)

    dataset_format = Column(String(50), nullable=True)

    status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    researcher_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )