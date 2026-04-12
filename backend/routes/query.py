import logging
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.gemini_service import (
    GEMINI_FAILURE_MESSAGE,
    GeminiGenerationError,
    generate_answer,
)
from services.rag import get_context

router = APIRouter()
logger = logging.getLogger(__name__)


class Message(BaseModel):
    role: str
    content: str


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    history: Optional[List[Message]] = None


class QueryResponse(BaseModel):
    answer: str


@router.post("/query", response_model=QueryResponse)
def query_rag(req: QueryRequest) -> QueryResponse:
    question = req.query.strip()

    if not question:
        return QueryResponse(answer=GEMINI_FAILURE_MESSAGE)

    try:
        logger.info("RAG question: %s", question)
        context = get_context(question)
        logger.info("RAG context:\n%s", context)

        answer = generate_answer(question=question, context=context)
        return QueryResponse(answer=answer)
    except GeminiGenerationError:
        logger.exception("Gemini failed to generate an answer.")
        return QueryResponse(answer=GEMINI_FAILURE_MESSAGE)
    except Exception:
        logger.exception("Query pipeline failed before a response could be generated.")
        return QueryResponse(answer=GEMINI_FAILURE_MESSAGE)
