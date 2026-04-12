import logging
import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_FAILURE_MESSAGE = "⚠️ Unable to generate answer. Please try again."
PROMPT_TEMPLATE = """You are a helpful assistant answering questions from retrieved documents.

Use only the provided context to answer the question.
You may combine details from multiple context sections and make reasonable inferences when they are directly supported by the context.
Do not add facts, assumptions, or outside knowledge.

Instructions:
- Give the direct answer first.
- Use clear, natural, human-friendly language.
- Use short paragraphs or bullets when they improve readability.
- Paraphrase the context instead of copying large passages.
- If the context partially answers the question, answer the supported part and clearly note what is missing.
- Say "I don't know based on the provided data." only when the context does not contain enough information to answer.

Context:
{context}

Question:
{question}

Answer:"""


class GeminiGenerationError(Exception):
    """Raised when Gemini fails to return a valid answer."""


def build_prompt(context: str, question: str) -> str:
    return PROMPT_TEMPLATE.format(context=context, question=question)


def _configure_model() -> genai.GenerativeModel:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise GeminiGenerationError("GEMINI_API_KEY is not configured.")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(GEMINI_MODEL)


def _extract_response_text(response) -> str:
    if response is None:
        raise GeminiGenerationError("Gemini returned no response.")

    candidates = getattr(response, "candidates", None) or []
    if candidates:
        first_candidate = candidates[0]
        content = getattr(first_candidate, "content", None)
        parts = getattr(content, "parts", None) or []

        text_parts = []
        for part in parts:
            text = getattr(part, "text", None)
            if isinstance(text, str) and text.strip():
                text_parts.append(text.strip())

        if text_parts:
            return "\n".join(text_parts).strip()

    try:
        text = response.text
    except Exception as exc:  # pragma: no cover - depends on Gemini SDK response state
        raise GeminiGenerationError("Gemini response did not contain readable text.") from exc

    if isinstance(text, str) and text.strip():
        return text.strip()

    raise GeminiGenerationError("Gemini returned an empty answer.")


def _sanitize_answer(answer: str) -> str:
    cleaned = answer.strip()

    for prefix in ("## Answer:", "Answer:"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].lstrip()

    cleaned_lines = [line.rstrip() for line in cleaned.splitlines() if line.strip()]
    cleaned = "\n".join(cleaned_lines).strip()

    if not cleaned:
        raise GeminiGenerationError("Gemini returned a blank answer after sanitization.")

    return cleaned


def generate_answer(question: str, context: str) -> str:
    """
    Generate a clean RAG answer from retrieved context and the user's question.

    Changes:
    - Uses a current supported Gemini Flash model first instead of the retired
      `models/gemini-1.5-pro` name that fails on the v1beta API.
    - Falls back across supported model families to avoid breaking the existing
      RAG pipeline if one model alias is unavailable in a given project.
    - Applies low-temperature generation so answers stay grounded in context.
    - Raises a controlled application error instead of leaking SDK failures.
    """
    prompt = build_prompt(context=context, question=question)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        logger.error("GEMINI_API_KEY is not configured.")
        raise GeminiGenerationError("Gemini generation failed.")

    genai.configure(api_key=api_key)

    # Google now documents Gemini 2.5 Flash as a stable model family. We keep
    # small fallbacks so the RAG pipeline remains available if a project/API key
    # has not rolled onto the newest alias yet.
    model_candidates = (
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    )

    last_error = None

    for model_name in model_candidates:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "max_output_tokens": 512,
                },
            )

            answer = _sanitize_answer(_extract_response_text(response))
            if not answer:
                raise GeminiGenerationError("Gemini returned an empty answer.")

            return answer
        except GeminiGenerationError as exc:
            last_error = exc
            logger.warning(
                "Gemini returned an unusable response with model %s: %s",
                model_name,
                exc,
            )
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Gemini request failed with model %s: %s",
                model_name,
                exc,
            )

    logger.error(
        "Gemini generation failed for question after trying %s. Last error: %s",
        model_candidates,
        last_error,
    )
    raise GeminiGenerationError("Gemini generation failed.") from last_error
