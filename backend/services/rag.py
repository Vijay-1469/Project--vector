import logging
from difflib import SequenceMatcher
from typing import Any

from embeddings.generate import get_query_embedding
from endee_client import search_similar

logger = logging.getLogger(__name__)

MIN_SIMILARITY_SCORE = 0.3
DEFAULT_TOP_K = 6
MAX_CONTEXT_WORDS = 1800
NEAR_DUPLICATE_THRESHOLD = 0.88


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _normalize_text(text: str) -> str:
    return " ".join(text.split()).strip().lower()


def _normalize_results(results: list[dict] | None) -> list[dict]:
    normalized_results = []

    for item in results or []:
        if not isinstance(item, dict):
            continue

        score = _safe_float(item.get("score", item.get("similarity", 0.0)))
        if score < MIN_SIMILARITY_SCORE:
            continue

        metadata = item.get("meta") or {}
        text = str(metadata.get("text", "")).strip()
        if not text:
            continue

        normalized_results.append(
            {
                "filename": str(metadata.get("filename", "unknown")),
                "page": metadata.get("page", 0),
                "score": round(score, 4),
                "text": text,
            }
        )

    return sorted(normalized_results, key=lambda item: item["score"], reverse=True)


def _is_near_duplicate(candidate: dict, selected: list[dict]) -> bool:
    candidate_text = _normalize_text(candidate["text"])
    if not candidate_text:
        return True

    for chunk in selected:
        if (
            candidate["filename"] != chunk["filename"]
            or candidate["page"] != chunk["page"]
        ):
            continue

        current_text = _normalize_text(chunk["text"])
        if candidate_text == current_text:
            return True

        if candidate_text in current_text or current_text in candidate_text:
            return True

        similarity = SequenceMatcher(None, candidate_text, current_text).ratio()
        if similarity >= NEAR_DUPLICATE_THRESHOLD:
            return True

    return False


def _dedupe_results(chunks: list[dict]) -> list[dict]:
    deduped_chunks = []

    for chunk in chunks:
        if _is_near_duplicate(chunk, deduped_chunks):
            continue
        deduped_chunks.append(chunk)

    return deduped_chunks


def _trim_to_word_limit(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).strip()


def _limit_context(chunks: list[dict], max_context_words: int = MAX_CONTEXT_WORDS) -> list[dict]:
    selected_chunks = []
    total_words = 0

    for chunk in chunks:
        chunk_word_count = len(chunk["text"].split())

        if not selected_chunks and chunk_word_count > max_context_words:
            selected_chunks.append(
                {
                    **chunk,
                    "text": _trim_to_word_limit(chunk["text"], max_context_words),
                }
            )
            break

        if total_words + chunk_word_count > max_context_words:
            continue

        selected_chunks.append(chunk)
        total_words += chunk_word_count

    return selected_chunks


def _format_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant context found."

    context_blocks = []
    for index, chunk in enumerate(chunks, start=1):
        context_blocks.append(
            (
                f"[Source {index}] {chunk['filename']} (page {chunk['page']})\n"
                f"{chunk['text']}"
            )
        )

    return "\n\n".join(context_blocks)


def get_context(question: str, top_k: int = DEFAULT_TOP_K) -> str:
    query_vector = get_query_embedding(question)
    results = search_similar(query_vector, top_k=top_k)
    normalized_results = _normalize_results(results)
    selected_chunks = _limit_context(_dedupe_results(normalized_results))

    logger.info(
        "Retrieved %s relevant chunks from Endee and kept %s after dedupe/budgeting.",
        len(normalized_results),
        len(selected_chunks),
    )
    return _format_context(selected_chunks)
