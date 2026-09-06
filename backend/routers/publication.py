from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.publication import Publication
from models.user import User
from schemas.publication import PublicationCreate, PublicationResponse
from auth import get_current_user


router = APIRouter(
    prefix="/publications",
    tags=["Publications"]
)


# =========================================================
# CREATE PUBLICATION
# POST /publications/
# =========================================================

@router.post("/", response_model=PublicationResponse)
def create_publication(
    publication: PublicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    new_publication = Publication(
        title=publication.title,
        authors=publication.authors,
        abstract=publication.abstract,
        journal=publication.journal,
        publication_year=publication.publication_year,
        doi=publication.doi,
        file_path=publication.file_path,
        researcher_id=current_user.id
    )

    try:
        db.add(new_publication)
        db.commit()
        db.refresh(new_publication)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create publication: {str(e)}"
        )

    return new_publication


# =========================================================
# GET ALL PUBLICATIONS
# GET /publications/
# =========================================================

@router.get("/", response_model=list[PublicationResponse])
def get_publications(
    db: Session = Depends(get_db)
):

    publications = (
        db.query(Publication)
        .order_by(Publication.created_at.desc())
        .all()
    )

    return publications


# =========================================================
# GET MY PUBLICATIONS
# GET /publications/my
# =========================================================

@router.get("/my", response_model=list[PublicationResponse])
def get_my_publications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    publications = (
        db.query(Publication)
        .filter(Publication.researcher_id == current_user.id)
        .order_by(Publication.created_at.desc())
        .all()
    )

    return publications


# =========================================================
# GET PUBLICATION BY ID
# GET /publications/{publication_id}
# =========================================================

@router.get("/{publication_id}", response_model=PublicationResponse)
def get_publication(
    publication_id: int,
    db: Session = Depends(get_db)
):

    publication = (
        db.query(Publication)
        .filter(Publication.id == publication_id)
        .first()
    )

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    return publication


# =========================================================
# UPDATE PUBLICATION
# PUT /publications/{publication_id}
# =========================================================

@router.put("/{publication_id}", response_model=PublicationResponse)
def update_publication(
    publication_id: int,
    publication_data: PublicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    publication = (
        db.query(Publication)
        .filter(Publication.id == publication_id)
        .first()
    )

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    # Only the owner can update
    if publication.researcher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own publication"
        )

    publication.title = publication_data.title
    publication.authors = publication_data.authors
    publication.abstract = publication_data.abstract
    publication.journal = publication_data.journal
    publication.publication_year = publication_data.publication_year
    publication.doi = publication_data.doi
    publication.file_path = publication_data.file_path

    try:
        db.commit()
        db.refresh(publication)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update publication: {str(e)}"
        )

    return publication


# =========================================================
# DELETE PUBLICATION
# DELETE /publications/{publication_id}
# =========================================================

@router.delete("/{publication_id}")
def delete_publication(
    publication_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    publication = (
        db.query(Publication)
        .filter(Publication.id == publication_id)
        .first()
    )

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    # Only the owner can delete
    if publication.researcher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own publication"
        )

    try:
        db.delete(publication)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete publication: {str(e)}"
        )

    return {
        "message": "Publication deleted successfully",
        "publication_id": publication_id
    }