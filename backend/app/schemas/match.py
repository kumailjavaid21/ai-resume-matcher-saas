from typing import List
from pydantic import BaseModel, Field


class JobDescriptionParse(BaseModel):
    role_title: str = Field(..., min_length=1)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    min_years: float = Field(0.0, ge=0)


class ResumeParse(BaseModel):
    skills: List[str] = Field(default_factory=list)
    experiences: List[str] = Field(default_factory=list)
    years_estimate: float = Field(0.0, ge=0)
    projects: List[str] = Field(default_factory=list)


class MatchResultSchema(BaseModel):
    resume_id: int
    score: float
    matched_skills: List[str]
    missing_required: List[str]
    missing_preferred: List[str]
    explanation: str
    improvement_suggestions: List[str]


class MatchResultsResponse(BaseModel):
    project_id: int
    jd: JobDescriptionParse
    matches: List[MatchResultSchema]


class MatchRunResponse(BaseModel):
    project_id: int
    total_matches: int
    best_score: float | None
