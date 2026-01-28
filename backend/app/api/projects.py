from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.dependencies import get_current_user, get_db
from backend.app.models.project import Project
from backend.app.schemas.project import ProjectCreate, ProjectRead

router = APIRouter()


@router.post("/projects", response_model=ProjectRead)
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    project = Project(user_id=user.id, title=project_data.title, description=project_data.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Project).filter(Project.user_id == user.id).all()
