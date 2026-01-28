import shutil
from pathlib import Path

from backend.app.core.config import settings


def save_upload_file(uploaded_file, user_id: int, project_id: int, doc_type: str) -> Path:
    base_dir = Path(settings.upload_dir) / str(user_id) / str(project_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    destination = base_dir / f"{doc_type}_{uploaded_file.filename}"
    with destination.open("wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return destination
