from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional


TraceType = Literal["plan", "tool", "reasoning", "answer", "system"]


class ThoughtStep(BaseModel):
    type: TraceType
    content: str
    ts: str


class SourceChunk(BaseModel):
    doc_id: str
    title: str
    snippet: str
    score: float = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    query: str
    stream: bool = True
    top_k: int = 3
    model_override: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    trace: List[ThoughtStep]
    sources: List[SourceChunk]
    usage: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: int


class SessionResponse(BaseModel):
    session_id: str


class ConfigResponse(BaseModel):
    provider: str
    model: str
    has_api_key: bool


class ConfigUpdateRequest(BaseModel):
    api_key: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
