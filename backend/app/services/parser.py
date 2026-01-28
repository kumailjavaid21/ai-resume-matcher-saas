import logging
from pathlib import Path

import pdfplumber
import requests
from fastapi import HTTPException, status
from pydantic import ValidationError
from pypdf import PdfReader

from backend.app.schemas.match import JobDescriptionParse, ResumeParse
from backend.app.services.ollama_client import OllamaClient

logger = logging.getLogger("parser")

JD_SCHEMA_HINT = """
Respond with a JSON object with the following fields:
- role_title (string)
- required_skills (array of strings)
- preferred_skills (array of strings)
- responsibilities (array of strings)
- min_years (number)
"""

RESUME_SCHEMA_HINT = """
Respond with a JSON object with the following fields:
- skills (array of strings)
- experiences (array of strings)
- years_estimate (number)
- projects (array of strings)
"""


def extract_text_from_pdf(path: Path) -> str:
    try:
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        logger.warning("PyPDF failed (%s), falling back to pdfplumber", exc)
    try:
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as exc:
        logger.error("pdfplumber extraction failed: %s", exc)
        raise


class DocumentParser:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client

    def _run_with_retry(self, text: str, schema_hint: str):
        try:
            return self.ollama.generate_json(text, schema_hint)
        except ValueError as exc:
            strict_text = f"{text}\nReturn ONLY JSON. No commentary."
            try:
                return self.ollama.generate_json(strict_text, schema_hint)
            except ValueError as strict_exc:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(strict_exc)) from strict_exc
        except requests.RequestException as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Ollama server not reachable at {self.ollama.base_url}",
            ) from exc

    def parse_jd(self, text: str) -> JobDescriptionParse:
        parsed = self._run_with_retry(text, JD_SCHEMA_HINT)
        try:
            return JobDescriptionParse(**parsed)
        except ValidationError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    def parse_resume(self, text: str) -> ResumeParse:
        parsed = self._run_with_retry(text, RESUME_SCHEMA_HINT)
        try:
            return ResumeParse(**parsed)
        except ValidationError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
