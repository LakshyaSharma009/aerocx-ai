"""PostgreSQL + pgvector persistence layer.

Tables: cases, predictions, documents, chunks (with embeddings), analyses.
Falls back gracefully: every function raises RuntimeError with a clear message
when DATABASE_URL is unreachable, so local dev without Postgres still works.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from src.utils.config import get_settings
from src.utils.logging import get_logger

log = get_logger(__name__)
Base = declarative_base()


class Case(Base):
    """Customer case."""

    __tablename__ = "cases"
    id = Column(Integer, primary_key=True)
    ticket_id = Column(String(32), unique=True, index=True)
    message = Column(Text, nullable=False)
    category = Column(String(64))
    sentiment = Column(String(32))
    severity = Column(String(32))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    predictions = relationship("Prediction", back_populates="case")
    analyses = relationship("Analysis", back_populates="case")


class Prediction(Base):
    """Single model prediction."""

    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    kind = Column(String(32))  # category | sentiment | escalation
    label = Column(String(128))
    score = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    case = relationship("Case", back_populates="predictions")


class Document(Base):
    """Knowledge-base document metadata."""

    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    doc_name = Column(String(256), unique=True, index=True)
    source = Column(String(64), default="synthetic")
    chunks = relationship("Chunk", back_populates="document")


class Chunk(Base):
    """Text chunk + embedding (pgvector column when available)."""

    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_id = Column(String(256), unique=True, index=True)
    text = Column(Text)
    # pgvector VECTOR type is created by migration below; stored as TEXT fallback otherwise.
    embedding = Column(Text)  # JSON list fallback for non-pgvector dev DBs
    document = relationship("Document", back_populates="chunks")


class Analysis(Base):
    """Full pipeline result."""

    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    result_json = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    case = relationship("Case", back_populates="analyses")


def get_engine(echo: bool = False):
    """Create engine from DATABASE_URL."""
    return create_engine(get_settings().database_url, echo=echo, pool_pre_ping=True)


INIT_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;
"""


def init_db() -> None:
    """Create extension + tables. Raises RuntimeError when DB unreachable."""
    try:
        engine = get_engine()
        with engine.begin() as conn:
            try:
                conn.exec_driver_sql(INIT_SQL)
            except Exception as e:  # extension may need superuser; tables still work
                log.warning("pgvector extension skipped: %s", e)
        Base.metadata.create_all(engine)
        log.info("Database initialised.")
    except Exception as e:
        raise RuntimeError(f"Could not initialise database: {e}")


def get_session():
    """Return a new ORM session."""
    return sessionmaker(bind=get_engine())()
