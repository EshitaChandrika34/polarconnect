from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.report import Report
from models.user import User
from schemas.report import ReportCreate, ReportResponse
from auth import get_current_user


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# =========================================================
# CREATE REPORT
# POST /reports/
# =========================================================

@router.post(
    "/",
    response_model=ReportResponse
)
def create_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    new_report = Report(
        title=report.title,
        description=report.description,
        file_path=report.file_path,

        # Always pending when created
        status="pending",

        # Use logged-in user
        researcher_id=current_user.id
    )

    try:
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create report: {str(e)}"
        )

    return new_report


# =========================================================
# GET ALL APPROVED REPORTS
# GET /reports/
# =========================================================

@router.get(
    "/",
    response_model=list[ReportResponse]
)
def get_reports(
    db: Session = Depends(get_db)
):

    reports = (
        db.query(Report)
        .filter(
            Report.status == "approved"
        )
        .order_by(
            Report.created_at.desc()
        )
        .all()
    )

    return reports


# =========================================================
# GET MY REPORTS
# GET /reports/my
# =========================================================

@router.get(
    "/my",
    response_model=list[ReportResponse]
)
def get_my_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    reports = (
        db.query(Report)
        .filter(
            Report.researcher_id == current_user.id
        )
        .order_by(
            Report.created_at.desc()
        )
        .all()
    )

    return reports


# =========================================================
# GET REPORT BY ID
# GET /reports/{report_id}
# =========================================================

@router.get(
    "/{report_id}",
    response_model=ReportResponse
)
def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):

    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return report


# =========================================================
# UPDATE REPORT
# PUT /reports/{report_id}
# =========================================================

@router.put(
    "/{report_id}",
    response_model=ReportResponse
)
def update_report(
    report_id: int,
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    # -----------------------------------------------------
    # ONLY OWNER CAN UPDATE
    # -----------------------------------------------------

    if report.researcher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own report"
        )

    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------

    report.title = report_data.title
    report.description = report_data.description
    report.file_path = report_data.file_path

    # Updated report requires approval again
    report.status = "pending"

    try:
        db.commit()
        db.refresh(report)

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to update report: {str(e)}"
        )

    return report


# =========================================================
# DELETE REPORT
# DELETE /reports/{report_id}
# =========================================================

@router.delete(
    "/{report_id}"
)
def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    # -----------------------------------------------------
    # ONLY OWNER CAN DELETE
    # -----------------------------------------------------

    if report.researcher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own report"
        )

    try:

        db.delete(report)
        db.commit()

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete report: {str(e)}"
        )

    return {
        "message": "Report deleted successfully",
        "report_id": report_id
    }