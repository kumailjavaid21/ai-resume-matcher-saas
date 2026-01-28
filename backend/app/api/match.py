from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.dependencies import get_current_user, get_db
from backend.app.models.document import Document
from backend.app.models.match_result import MatchResult
from backend.app.models.project import Project
from backend.app.schemas.match import JobDescriptionParse, MatchResultSchema, MatchResultsResponse, MatchRunResponse
from backend.app.services.matcher import Matcher
from backend.app.services.report import generate_project_report
from backend.app.core.config import settings

router = APIRouter()
matcher = Matcher()


def _authorize_project(db: Session, project_id: int, user_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_jd_document(db: Session, project_id: int) -> Document:
    doc = (
        db.query(Document)
        .filter(Document.project_id == project_id, Document.doc_type == "job_description")
        .order_by(Document.id.desc())
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Job description not uploaded")
    return doc


def _get_resume_documents(db: Session, project_id: int) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.project_id == project_id, Document.doc_type == "resume")
        .order_by(Document.id)
        .all()
    )


@router.post("/match/run", response_model=MatchRunResponse)
def run_matching(project_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    _authorize_project(db, project_id, user.id)
    jd_doc = _get_jd_document(db, project_id)
    resumes = _get_resume_documents(db, project_id)
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes uploaded")
    db.query(MatchResult).filter(MatchResult.project_id == project_id).delete()
    db.commit()
    parsed_jd = JobDescriptionParse(**jd_doc.parsed_json)
    matches = []
    for resume in resumes:
        schema = matcher.match(jd_doc, resume)
        match_record = MatchResult(
            project_id=project_id,
            resume_document_id=resume.id,
            score=schema.score,
            matched_skills=schema.matched_skills,
            missing_required=schema.missing_required,
            missing_preferred=schema.missing_preferred,
            explanation=schema.explanation,
            improvement_suggestions=schema.improvement_suggestions,
        )
        db.add(match_record)
        matches.append(schema)
    db.commit()
    best_score = max((m.score for m in matches), default=None)
    generate_project_report(project_id, parsed_jd, matches)
    return MatchRunResponse(project_id=project_id, total_matches=len(matches), best_score=best_score)


@router.get("/match/results", response_model=MatchResultsResponse)
def get_match_results(project_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    _authorize_project(db, project_id, user.id)
    jd_doc = _get_jd_document(db, project_id)
    parsed_jd = JobDescriptionParse(**jd_doc.parsed_json)
    results = (
        db.query(MatchResult)
        .filter(MatchResult.project_id == project_id)
        .order_by(MatchResult.score.desc())
        .all()
    )
    matches = [
        MatchResultSchema(
            resume_id=result.resume_document_id,
            score=result.score,
            matched_skills=result.matched_skills,
            missing_required=result.missing_required,
            missing_preferred=result.missing_preferred,
            explanation=result.explanation,
            improvement_suggestions=result.improvement_suggestions,
        )
        for result in results
    ]
    return MatchResultsResponse(project_id=project_id, jd=parsed_jd, matches=matches)


@router.get("/reports/{project_id}.pdf")
def download_report(project_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    _authorize_project(db, project_id, user.id)
    path = Path(settings.report_dir) / f"project_{project_id}_report.pdf"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Report not generated yet")
    return FileResponse(path, media_type="application/pdf", filename=path.name)
