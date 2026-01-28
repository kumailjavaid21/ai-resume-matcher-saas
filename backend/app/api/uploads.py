from typing import List

import requests
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.dependencies import get_current_user, get_db
from backend.app.models.document import Document
from backend.app.models.project import Project
from backend.app.schemas.document import DocumentRead
from backend.app.schemas.match import JobDescriptionParse, ResumeParse
from backend.app.services.ollama_client import OllamaClient
from backend.app.services.parser import DocumentParser, extract_text_from_pdf
from backend.app.services.storage import save_upload_file

router = APIRouter()

ollama_client = OllamaClient()
parser = DocumentParser(ollama_client)


def _embed_text(text: str) -> list[float]:
    try:
        return ollama_client.embed(text)
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama server not reachable at {ollama_client.base_url}",
        ) from exc


def get_project_or_404(project_id: int, user_id: int, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("/upload/jd", response_model=DocumentRead)
def upload_job_description(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    project = get_project_or_404(project_id, user.id, db)
    saved = save_upload_file(file, user.id, project_id, "jd")
    text = extract_text_from_pdf(saved)
    parsed: JobDescriptionParse = parser.parse_jd(text)
    embedding = _embed_text(text)
    document = Document(
        project_id=project.id,
        user_id=user.id,
        doc_type="job_description",
        filename=file.filename,
        filepath=str(saved),
        raw_text=text,
        parsed_json=parsed.dict(),
        embedding=embedding,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.post("/upload/resumes", response_model=list[DocumentRead])
def upload_resumes(project_id: int, files: List[UploadFile] = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    project = get_project_or_404(project_id, user.id, db)
    documents = []
    for file in files:
        saved = save_upload_file(file, user.id, project_id, "resume")
        text = extract_text_from_pdf(saved)
        parsed: ResumeParse = parser.parse_resume(text)
        embedding = _embed_text(text)
        document = Document(
            project_id=project.id,
            user_id=user.id,
            doc_type="resume",
            filename=file.filename,
            filepath=str(saved),
            raw_text=text,
            parsed_json=parsed.dict(),
            embedding=embedding,
        )
        db.add(document)
        documents.append(document)
    db.commit()
    for document in documents:
        db.refresh(document)
    return documents
