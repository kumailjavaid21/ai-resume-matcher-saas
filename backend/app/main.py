from fastapi import FastAPI

from backend.app.api.auth import router as auth_router
from backend.app.api.match import router as match_router
from backend.app.api.projects import router as projects_router
from backend.app.api.uploads import router as uploads_router
from backend.app.core.database import init_db

app = FastAPI(title="AI Resume Matcher")


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(uploads_router)
app.include_router(match_router)
