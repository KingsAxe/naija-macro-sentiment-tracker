from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RawText(Base):
    __tablename__ = "raw_texts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(100), index=True)
    topic_label: Mapped[str | None] = mapped_column(String(150), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    sentiment: Mapped[AnalyzedSentiment | None] = relationship(
        back_populates="raw_text",
        cascade="all, delete-orphan",
        uselist=False,
    )


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_type: Mapped[str] = mapped_column(String(50), index=True)
    source_name: Mapped[str | None] = mapped_column(String(150), nullable=True, index=True)
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), index=True)
    fetched_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    inserted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    qa_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AnalyzedSentiment(Base):
    __tablename__ = "analyzed_sentiments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    raw_text_id: Mapped[int] = mapped_column(ForeignKey("raw_texts.id"), unique=True, nullable=False)
    overall_sentiment: Mapped[str] = mapped_column(String(50), index=True)
    confidence_positive: Mapped[float] = mapped_column(Float, default=0.0)
    confidence_neutral: Mapped[float] = mapped_column(Float, default=0.0)
    confidence_negative: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    raw_text: Mapped[RawText] = relationship(back_populates="sentiment")
    opinion_targets: Mapped[list[OpinionTarget]] = relationship(
        back_populates="analyzed_sentiment",
        cascade="all, delete-orphan",
    )


class OpinionTarget(Base):
    __tablename__ = "opinion_targets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    analyzed_sentiment_id: Mapped[int] = mapped_column(
        ForeignKey("analyzed_sentiments.id"),
        nullable=False,
        index=True,
    )
    target_name: Mapped[str] = mapped_column(String(200), index=True)
    target_sentiment: Mapped[str] = mapped_column(String(50), index=True)

    analyzed_sentiment: Mapped[AnalyzedSentiment] = relationship(back_populates="opinion_targets")
    assessments: Mapped[list[OpinionAssessment]] = relationship(
        back_populates="opinion_target",
        cascade="all, delete-orphan",
    )


class OpinionAssessment(Base):
    __tablename__ = "opinion_assessments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    opinion_target_id: Mapped[int] = mapped_column(
        ForeignKey("opinion_targets.id"),
        nullable=False,
        index=True,
    )
    assessment_text: Mapped[str] = mapped_column(String(200), index=True)
    assessment_sentiment: Mapped[str] = mapped_column(String(50), index=True)

    opinion_target: Mapped[OpinionTarget] = relationship(back_populates="assessments")
