from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON, Float, Text
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    resume_document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    score = Column(Float, nullable=False)
    matched_skills = Column(JSON, default=list)
    missing_required = Column(JSON, default=list)
    missing_preferred = Column(JSON, default=list)
    explanation = Column(Text, default="")
    improvement_suggestions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="matches")
    resume_document = relationship("Document")
