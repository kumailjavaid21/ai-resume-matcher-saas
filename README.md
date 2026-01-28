# AI Resume Matcher

FastAPI backend + Streamlit frontend SaaS scaffold that matches job descriptions against candidate resumes using only local Ollama models.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, SQLite, JWT, bcrypt, Ollama HTTP API, ReportLab
- **AI:** Ollama endpoints (`/api/generate`, `/api/embeddings`) with `llama3.1:8b` chat + `nomic-embed-text` embeddings
- **Frontend:** Streamlit multi-page experience
- **Tests:** Pytest covering auth and uploads

## Local Setup

1. Copy the example environment variables:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run Ollama locally (make sure the models referenced in `.env` are already installed):
   ```bash
   ollama serve
   ```
4. Start the backend API:
   ```bash
   cd backend
   uvicorn backend.app.main:app --reload --port 8000
   ```
5. In a new terminal, launch the Streamlit frontend:
   ```bash
   streamlit run frontend/streamlit_app.py
   ```

## Screenshots

- Backend dashboard placeholder: `frontend/assets/backend.png`
- Streamlit login placeholder: `frontend/assets/login.png`
- Match results placeholder: `frontend/assets/results.png`

## Testing

```bash
pytest
```

## API Endpoints

| Route | Method | Description |
| --- | --- | --- |
| `/auth/signup` | POST | Register user & receive JWT |
| `/auth/login` | POST | Authenticate user |
| `/projects` | POST/GET | Manage projects |
| `/upload/jd` | POST | Upload job description PDF |
| `/upload/resumes` | POST | Upload resumes |
| `/match/run` | POST | Compute matching results |
| `/match/results` | GET | Retrieve scored matches |
| `/reports/{project_id}.pdf` | GET | Download consolidated PDF report |

## Docker (optional)

Build and run backend with Docker:

```bash
docker build -t ai-resume-matcher .
docker run --env-file .env -p 8000:8000 ai-resume-matcher
```

This does not bundle Ollama—you still need to run `ollama serve` locally as described above.
