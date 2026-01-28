import math
from typing import List

import numpy as np
from backend.app.models.document import Document
from backend.app.models.match_result import MatchResult
from backend.app.schemas.match import JobDescriptionParse, MatchResultSchema, ResumeParse


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    arr_a = np.array(a, dtype=float)
    arr_b = np.array(b, dtype=float)
    denom = (math.sqrt(np.dot(arr_a, arr_a)) * math.sqrt(np.dot(arr_b, arr_b)))
    if denom == 0:
        return 0.0
    return float(np.dot(arr_a, arr_b) / denom)


def _overlap_score(source: List[str], target: List[str]) -> List[str]:
    normalized_source = {skill.strip().lower() for skill in source}
    normalized_target = {skill.strip().lower() for skill in target}
    matched = [skill for skill in source if skill.strip().lower() in normalized_target]
    return matched


class Matcher:
    def __init__(self):
        pass

    def match(self, jd_doc: Document, resume_doc: Document) -> MatchResultSchema:
        jd_data = JobDescriptionParse(**jd_doc.parsed_json)
        resume_data = ResumeParse(**resume_doc.parsed_json)

        matched_required = _overlap_score(jd_data.required_skills, resume_data.skills)
        matched_preferred = _overlap_score(jd_data.preferred_skills, resume_data.skills)
        missing_required = [s for s in jd_data.required_skills if s not in matched_required]
        missing_preferred = [s for s in jd_data.preferred_skills if s not in matched_preferred]

        required_score = 1.0 if not jd_data.required_skills else len(matched_required) / len(jd_data.required_skills)
        preferred_score = 1.0 if not jd_data.preferred_skills else len(matched_preferred) / len(jd_data.preferred_skills)

        embedding_similarity = _cosine_similarity(jd_doc.embedding or [], resume_doc.embedding or []) * 0.5 + 0.5
        exp_gap = abs(resume_data.years_estimate - jd_data.min_years)
        experience_score = 1 - min(exp_gap / max(jd_data.min_years or 1, 1), 1)

        weighted = (
            45 * required_score
            + 15 * preferred_score
            + 25 * embedding_similarity
            + 15 * experience_score
        )
        score = round(min(max(weighted, 0), 100), 2)

        explanation = (
            f"{resume_doc.filename} matches {len(matched_required)} required and {len(matched_preferred)} preferred skills "
            f"with an embedding similarity of {embedding_similarity:.2f}. Experience estimate is {resume_data.years_estimate} years "
            f"against the minimum {jd_data.min_years} years."
        )

        suggestions = []
        if resume_data.experiences:
            experience_sample = resume_data.experiences[0]
            suggestions.append(
                f"Rephrase the experience '{experience_sample}' to foreground the matched skills: "
                f"{', '.join(matched_required + matched_preferred) or 'relevant keywords'}."
            )
        if resume_data.projects:
            project_sample = resume_data.projects[0]
            suggestions.append(f"Highlight the project '{project_sample}' with achievements tied back to the role title '{jd_data.role_title}'.")

        return MatchResultSchema(
            resume_id=resume_doc.id,
            score=score,
            matched_skills=matched_required + matched_preferred,
            missing_required=missing_required,
            missing_preferred=missing_preferred,
            explanation=explanation,
            improvement_suggestions=suggestions,
        )
