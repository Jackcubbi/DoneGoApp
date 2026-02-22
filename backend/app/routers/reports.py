from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.weekly_report import WeeklyReport
from app.models.work_entry import WorkEntry
from app.models.work_code import WorkCode
from app.models.user import User
from app.schemas.report import ReportCreate, ReportUpdate, ReportOut
from app.dependencies import get_current_user
from app.services.pdf import generate_report_pdf
from app.services.whatsapp import send_whatsapp_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _get_own_report(report_id: int, db: Session, user: User) -> WeeklyReport:
    report = (
        db.query(WeeklyReport)
        .filter(WeeklyReport.id == report_id, WeeklyReport.user_id == user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


def _get_wc_map(db: Session, user_id: int) -> dict[int, str]:
    codes = (
        db.query(WorkCode)
        .filter((WorkCode.user_id == None) | (WorkCode.user_id == user_id))
        .all()
    )
    return {wc.code: wc.description for wc in codes}


@router.get("", response_model=list[ReportOut])
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(WeeklyReport)
        .filter(WeeklyReport.user_id == current_user.id)
        .order_by(WeeklyReport.year.desc(), WeeklyReport.week_number.desc())
        .all()
    )


@router.post("", response_model=ReportOut, status_code=201)
def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = WeeklyReport(
        user_id=current_user.id,
        project_id=payload.project_id,
        week_number=payload.week_number,
        year=payload.year,
        status=payload.status,
    )
    db.add(report)
    db.flush()
    for e in payload.entries:
        db.add(WorkEntry(
            report_id=report.id, day=e.day, hours=e.hours,
            area=e.area, objects=e.objects,
            description=e.description, work_code=e.work_code,
        ))
    db.commit()
    db.refresh(report)
    return report


@router.get("/{report_id}", response_model=ReportOut)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_own_report(report_id, db, current_user)


@router.put("/{report_id}", response_model=ReportOut)
def update_report(
    report_id: int,
    payload: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = _get_own_report(report_id, db, current_user)
    if payload.week_number is not None:
        report.week_number = payload.week_number
    if payload.year is not None:
        report.year = payload.year
    if payload.project_id is not None:
        report.project_id = payload.project_id
    if payload.entries is not None:
        for entry in list(report.entries):
            db.delete(entry)
        db.flush()
        for e in payload.entries:
            db.add(WorkEntry(
                report_id=report.id, day=e.day, hours=e.hours,
                area=e.area, objects=e.objects,
                description=e.description, work_code=e.work_code,
            ))
    report.status = "saved"
    db.commit()
    db.refresh(report)
    return report


@router.get("/{report_id}/pdf")
def download_pdf(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = _get_own_report(report_id, db, current_user)
    wc_map = _get_wc_map(db, current_user.id)
    pdf_bytes = generate_report_pdf(report, wc_map, current_user)
    filename = f"report_week{report.week_number}_{report.year}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{report_id}/send")
def send_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = _get_own_report(report_id, db, current_user)
    wc_map = _get_wc_map(db, current_user.id)
    pdf_bytes = generate_report_pdf(report, wc_map, current_user)
    filename = f"report_week{report.week_number}_{report.year}.pdf"
    message = (
        f"📋 Weekly Report\n"
        f"Worker: {current_user.name} {current_user.surname}\n"
        f"Week: {report.week_number} / {report.year}"
    )
    send_whatsapp_report(pdf_bytes, filename, message)
    report.status = "sent"
    db.commit()
    return {"detail": "Report sent successfully"}


@router.delete("/{report_id}", status_code=204)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = _get_own_report(report_id, db, current_user)
    db.delete(report)
    db.commit()
