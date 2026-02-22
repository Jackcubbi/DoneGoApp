from collections import defaultdict
from datetime import date, timedelta

from fpdf import FPDF

from app.models.weekly_report import WeeklyReport
from app.models.user import User

DAYS = ["Ma", "Ti", "Ke", "To", "Pe", "La", "Su"]
ROW_H = 7   # mm – compact enough to fit 14+ rows on one A4 page


def _week_dates(week: int, year: int) -> dict[str, str]:
    jan4 = date(year, 1, 4)
    monday = jan4 - timedelta(days=jan4.weekday()) + timedelta(weeks=week - 1)
    return {DAYS[i]: (monday + timedelta(days=i)).strftime("%d.%m") for i in range(7)}


def _meta_row(pdf: FPDF, label: str, value: str, usable: float) -> None:
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(36, 4.5, label + ":", ln=False)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(usable - 36, 4.5, value, ln=True)


def generate_report_pdf(report: WeeklyReport, work_code_map: dict[int, str], user: User) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(14, 14, 14)
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()

    usable = pdf.w - pdf.l_margin - pdf.r_margin   # ~182 mm
    DAY_W = 22
    col_w = [DAY_W, 19, 19, 28, usable - DAY_W - 66]

    dates = _week_dates(report.week_number, report.year)

    # ── Title ──────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, f"VIIKKORAPORTTI - VIIKKO {report.week_number} / {report.year}", align="C", ln=True)
    pdf.ln(2)

    # ── Meta block ─────────────────────────────────────────────
    _meta_row(pdf, "Tyontekija", f"{user.name} {user.surname}", usable)

    p = report.project
    if p:
        name_str = p.name or ""
        if p.project_code:
            name_str = f"{p.project_code} - {name_str}"
        _meta_row(pdf, "Projekti", name_str, usable)
        if p.address:
            _meta_row(pdf, "Osoite", p.address, usable)
        if p.general_company:
            _meta_row(pdf, "Paaurakoitsija", p.general_company, usable)
        if p.employer:
            _meta_row(pdf, "Tyonantaja", p.employer, usable)

    pdf.ln(3)

    # ── Table header ───────────────────────────────────────────
    headers = ["Paiva", "Tunnit", "m/m2", "Tyoalue", "Tyovaihe / Tyonkuvaus"]
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(44, 62, 80)
    pdf.set_text_color(255, 255, 255)
    for w, h in zip(col_w, headers):
        pdf.cell(w, 6, h, border=1, fill=True)
    pdf.ln()

    # ── Data rows ──────────────────────────────────────────────
    entries_by_day: dict[str, list] = defaultdict(list)
    for e in report.entries:
        entries_by_day[e.day].append(e)

    total_hours = 0.0
    total_area = 0.0
    row_num = 0

    for day in DAYS:
        day_entries = entries_by_day.get(day, [])
        rows = day_entries if day_entries else [None]
        n = len(rows)

        for sub_idx, entry in enumerate(rows):
            is_first = sub_idx == 0
            is_last  = sub_idx == n - 1
            fill = row_num % 2 == 1

            pdf.set_fill_color(248, 249, 250)
            pdf.set_text_color(0, 0, 0)

            x0, y0 = pdf.get_x(), pdf.get_y()

            # ── Day column border box ──
            if n == 1:
                day_border = 1          # all four sides
            elif is_first:
                day_border = "LTR"      # no bottom – merged visually with rows below
            elif is_last:
                day_border = "LBR"      # no top
            else:
                day_border = "LR"       # no top/bottom

            pdf.set_font("Helvetica", "", 8)
            pdf.cell(DAY_W, ROW_H, "", border=day_border, fill=fill)
            pdf.set_xy(x0 + DAY_W, y0)   # advance X past day col, keep Y

            # ── Overlay day name + date on first sub-row only ──
            if is_first:
                pdf.set_xy(x0 + 1.5, y0 + 0.5)
                pdf.set_font("Helvetica", "B", 7)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(DAY_W - 3, 3, day)

                pdf.set_xy(x0 + 1.5, y0 + 3.5)
                pdf.set_font("Helvetica", "", 6)
                pdf.set_text_color(120, 120, 120)
                pdf.cell(DAY_W - 3, 3, dates[day])
                pdf.set_text_color(0, 0, 0)

                pdf.set_xy(x0 + DAY_W, y0)  # restore cursor for data cells

            # ── Data cells ──
            if entry:
                hours_str   = entry.hours       if entry.hours       else "-"
                area_str    = entry.area        if entry.area        else "-"
                objects_str = entry.objects     if entry.objects     else "-"
                if entry.work_code:
                    wc_desc  = work_code_map.get(entry.work_code, "")
                    tyovaihe = f"{entry.work_code} - {wc_desc}" if wc_desc else str(entry.work_code)
                elif entry.description:
                    tyovaihe = entry.description
                else:
                    tyovaihe = "-"
                try:    total_hours += float(hours_str)
                except (ValueError, TypeError): pass
                try:    total_area  += float(area_str)
                except (ValueError, TypeError): pass
            else:
                hours_str = area_str = objects_str = tyovaihe = "-"

            pdf.set_font("Helvetica", "", 8)
            for w, v in zip(col_w[1:], [hours_str, area_str, objects_str, tyovaihe]):
                pdf.cell(w, ROW_H, str(v), border=1, fill=fill)
            pdf.ln()
            row_num += 1

    # ── Summary row ────────────────────────────────────────────
    def fmt(n: float) -> str:
        return str(int(n)) if n == int(n) else str(round(n, 2))

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(220, 228, 237)
    pdf.set_text_color(0, 0, 0)
    for w, v in zip(col_w, ["Yhteensa", fmt(total_hours), fmt(total_area), "", ""]):
        pdf.cell(w, 6, v, border=1, fill=True)
    pdf.ln()

    # ── Work-code legend ───────────────────────────────────────
    used_codes = sorted({e.work_code for e in report.entries if e.work_code})
    if used_codes:
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 4, "Tyovaihe:", ln=True)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(0, 0, 0)
        for c in used_codes:
            pdf.cell(0, 4, f"  {c} = {work_code_map.get(c, '?')}", ln=True)

    # ── Footer ────────────────────────────────────────────────
    pdf.set_y(-14)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(0, 5, "DoneGo / Urakka Work Tracker", align="R")

    return bytes(pdf.output())
