from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agents.agent import run_agent

router = APIRouter()


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]]
    trace: list[str]


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    response = run_agent(request.query)
    return ChatResponse(answer=response.answer, sources=response.sources, trace=response.trace)


@router.post("/search", response_model=ChatResponse)
def search(request: ChatRequest) -> ChatResponse:
    """Alias used by the UI language: edited text is sent to financial search."""
    return chat(request)
