from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from database import Base


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    authors = Column(String(500), nullable=True)
    abstract = Column(Text, nullable=True)

    journal = Column(String(255), nullable=True)
    publication_year = Column(Integer, nullable=True)

    doi = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)

    researcher_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )