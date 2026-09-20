"""Pydantic request/response schemas for the AeroCX API."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class CategoryRequest(BaseModel):
    """Classify a customer message."""

    message: str = Field(..., min_length=3, max_length=5000)


class CategoryResponse(BaseModel):
    """Predicted issue category."""

    category: str
    confidence: float


class SentimentRequest(BaseModel):
    """Sentiment request."""

    message: str = Field(..., min_length=1, max_length=5000)


class SentimentResponse(BaseModel):
    """Sentiment result."""

    sentiment_label: str
    sentiment_score: float
    provider: str = "unknown"


class EscalationRequest(BaseModel):
    """Structured escalation features."""

    message: str = Field(..., min_length=3, max_length=5000)
    category: str = "Other"
    sentiment: str = "neutral"
    severity: str = "medium"
    delay_hours: float = 0.0
    previous_complaints: int = 0
    customer_priority: str = "standard"
    aircraft_type: str = "A320neo"


class EscalationResponse(BaseModel):
    """Escalation result."""

    escalation_probability: float
    risk_level: str
    important_factors: List[dict] = []


class AnalyzeRequest(BaseModel):
    """Full case-analysis request."""

    message: str = Field(..., min_length=3, max_length=5000)
    delay_hours: float = 0.0
    previous_complaints: int = 0
    customer_priority: str = "standard"
    aircraft_type: str = "A320neo"


class SourceRef(BaseModel):
    """Retrieved source reference."""

    doc_name: str
    chunk_id: str = ""
    score: float = 0.0


class AnalyzeResponse(BaseModel):
    """Unified case-analysis response."""

    category: str
    category_confidence: float = 0.0
    sentiment: str
    sentiment_score: float
    severity: str
    escalation_probability: float
    risk_level: str
    recommended_action: str
    generated_response: str
    sources: List[str] = []
    important_factors: List[dict] = []


class RagQueryRequest(BaseModel):
    """Standalone knowledge-base query."""

    query: str = Field(..., min_length=3, max_length=2000)
    top_k: int = Field(4, ge=1, le=10)


class RagQueryResponse(BaseModel):
    """Grounded answer plus sources."""

    answer: str
    sources: List[str]
    provider: str
    retrieved: List[SourceRef] = []


class HealthResponse(BaseModel):
    """Health check."""

    status: str = "ok"
    models_loaded: dict = {}
    rag_ready: bool = False


class ErrorResponse(BaseModel):
    """Error envelope."""

    detail: str


OptionalStr = Optional[str]
