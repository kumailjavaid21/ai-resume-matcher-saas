from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

from backend.app.core.config import settings
from backend.app.schemas.match import JobDescriptionParse, MatchResultSchema


def generate_project_report(project_id: int, jd: JobDescriptionParse, matches: list[MatchResultSchema]) -> Path:
    report_dir = Path(settings.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    target = report_dir / f"project_{project_id}_report.pdf"
    c = canvas.Canvas(str(target), pagesize=LETTER)
    width, height = LETTER
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 60, f"AI Resume Matcher Report — Project {project_id}")
    c.setFont("Helvetica", 12)
    c.drawString(40, height - 90, f"Role: {jd.role_title}")

    y = height - 130
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Job Description Summary")
    c.setFont("Helvetica", 10)
    y -= 20
    for label, values in [
        ("Required skills", jd.required_skills),
        ("Preferred skills", jd.preferred_skills),
        ("Responsibilities", jd.responsibilities),
    ]:
        c.drawString(50, y, f"{label}: {', '.join(values)}")
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 50
    c.drawString(40, y, f"Minimum Years Experience: {jd.min_years}")
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Resume Matches")
    y -= 20
    c.setFont("Helvetica", 10)
    for match in matches:
        c.drawString(50, y, f"Resume ID: {match.resume_id} — Score: {match.score}")
        y -= 12
        c.drawString(60, y, f"Matched skills: {', '.join(match.matched_skills)}")
        y -= 12
        c.drawString(60, y, f"Missing required skills: {', '.join(match.missing_required) or 'None'}")
        y -= 12
        c.drawString(60, y, f"Missing preferred skills: {', '.join(match.missing_preferred) or 'None'}")
        y -= 12
        c.drawString(60, y, f"Suggestions: {'; '.join(match.improvement_suggestions)}")
        y -= 25
        if y < 100:
            c.showPage()
            y = height - 50
    c.save()
    return target
