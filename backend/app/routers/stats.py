from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.weekly_report import WeeklyReport
from app.models.work_entry import WorkEntry
from app.models.work_code import WorkCode
from app.models.project import Project
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Overall totals: hours, area, report count by status."""
    reports = (
        db.query(WeeklyReport)
        .filter(WeeklyReport.user_id == current_user.id)
        .all()
    )
    total_hours = 0.0
    total_area = 0.0
    status_counts = {"draft": 0, "saved": 0, "sent": 0}

    for report in reports:
        status_counts[report.status] = status_counts.get(report.status, 0) + 1
        for entry in report.entries:
            if report.status in ("saved", "sent"):
                try:
                    total_hours += float(entry.hours or 0)
                except (TypeError, ValueError):
                    pass
                try:
                    total_area += float(entry.area or 0)
                except (TypeError, ValueError):
                    pass

    project_count = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .count()
    )

    return {
        "total_hours": round(total_hours, 2),
        "total_area": round(total_area, 2),
        "report_count": len(reports),
        "project_count": project_count,
        "status_counts": status_counts,
    }


@router.get("/by-week")
def get_by_week(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Hours and area totals grouped by year+week (most recent 20 weeks)."""
    reports = (
        db.query(WeeklyReport)
        .filter(
            WeeklyReport.user_id == current_user.id,
            WeeklyReport.status.in_(["saved", "sent"]),
        )
        .order_by(WeeklyReport.year.asc(), WeeklyReport.week_number.asc())
        .all()
    )

    week_map: dict[str, dict] = {}
    for report in reports:
        key = f"{report.year}-V{report.week_number:02d}"
        if key not in week_map:
            week_map[key] = {"label": key, "hours": 0.0, "area": 0.0}
        for entry in report.entries:
            try:
                week_map[key]["hours"] += float(entry.hours or 0)
            except (TypeError, ValueError):
                pass
            try:
                week_map[key]["area"] += float(entry.area or 0)
            except (TypeError, ValueError):
                pass

    result = [
        {**v, "hours": round(v["hours"], 2), "area": round(v["area"], 2)}
        for v in week_map.values()
    ]
    # Return last 20 weeks
    return result[-20:]


@router.get("/by-project")
def get_by_project(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Hours grouped by project."""
    reports = (
        db.query(WeeklyReport)
        .filter(
            WeeklyReport.user_id == current_user.id,
            WeeklyReport.status.in_(["saved", "sent"]),
        )
        .all()
    )

    projects = {
        p.id: (f"{p.project_code} – {p.name}" if p.project_code else p.name)
        for p in db.query(Project).filter(Project.user_id == current_user.id).all()
    }

    project_map: dict[str, float] = {}
    for report in reports:
        label = projects.get(report.project_id, "Ei projektia")
        if label not in project_map:
            project_map[label] = 0.0
        for entry in report.entries:
            try:
                project_map[label] += float(entry.hours or 0)
            except (TypeError, ValueError):
                pass

    return [
        {"label": k, "hours": round(v, 2)}
        for k, v in sorted(project_map.items(), key=lambda x: -x[1])
    ]


@router.get("/by-workcode")
def get_by_workcode(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Hours grouped by work code."""
    reports = (
        db.query(WeeklyReport)
        .filter(
            WeeklyReport.user_id == current_user.id,
            WeeklyReport.status.in_(["saved", "sent"]),
        )
        .all()
    )

    work_codes = {
        wc.code: f"{wc.code} – {wc.description}"
        for wc in db.query(WorkCode)
        .filter((WorkCode.user_id == None) | (WorkCode.user_id == current_user.id))
        .all()
    }

    code_map: dict[str, float] = {}
    for report in reports:
        for entry in report.entries:
            if entry.work_code is None:
                continue
            label = work_codes.get(entry.work_code, f"Koodi {entry.work_code}")
            if label not in code_map:
                code_map[label] = 0.0
            try:
                code_map[label] += float(entry.hours or 0)
            except (TypeError, ValueError):
                pass

    return [
        {"label": k, "hours": round(v, 2)}
        for k, v in sorted(code_map.items(), key=lambda x: -x[1])
    ]
