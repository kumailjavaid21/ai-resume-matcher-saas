from contextlib import contextmanager
from io import BytesIO

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from backend.app.api import uploads as uploads_module
from backend.app.main import app
from backend.app.schemas.match import JobDescriptionParse, ResumeParse

client = TestClient(app)


def make_pdf_stream(text: str) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, text)
    c.save()
    buffer.seek(0)
    return buffer


@contextmanager
def patched_parser():
    original_parse_jd = uploads_module.parser.parse_jd
    original_parse_resume = uploads_module.parser.parse_resume
    original_embed = uploads_module.ollama_client.embed

    uploads_module.parser.parse_jd = lambda text: JobDescriptionParse(
        role_title="Test Engineer",
        required_skills=["python"],
        preferred_skills=["fastapi"],
        responsibilities=["Build services"],
        min_years=2.0,
    )
    uploads_module.parser.parse_resume = lambda text: ResumeParse(
        skills=["python", "fastapi"],
        experiences=["Built API"],
        years_estimate=3.0,
        projects=["Resume Builder"],
    )
    uploads_module.ollama_client.embed = lambda text: [0.1] * 384
    try:
        yield
    finally:
        uploads_module.parser.parse_jd = original_parse_jd
        uploads_module.parser.parse_resume = original_parse_resume
        uploads_module.ollama_client.embed = original_embed


def test_upload_endpoints_work():
    email = "upload-test@example.com"
    password = "secret"
    client.post("/auth/signup", json={"email": email, "password": password})
    login_resp = client.post("/auth/login", json={"email": email, "password": password})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    project_resp = client.post("/projects", json={"title": "Upload Test", "description": ""}, headers=headers)
    project_id = project_resp.json()["id"]

    with patched_parser():
        jd_pdf = make_pdf_stream("Job description content")
        jd_upload = client.post(
            f"/upload/jd?project_id={project_id}",
            files={"file": ("jd.pdf", jd_pdf, "application/pdf")},
            headers=headers,
        )
        assert jd_upload.status_code == 200

        resume_pdf = make_pdf_stream("Resume content")
        resume_upload = client.post(
            f"/upload/resumes?project_id={project_id}",
            files=[("files", ("resume.pdf", resume_pdf, "application/pdf"))],
            headers=headers,
        )
        assert resume_upload.status_code == 200
