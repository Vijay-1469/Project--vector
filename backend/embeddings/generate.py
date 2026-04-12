import warnings
from functools import lru_cache

from sentence_transformers import SentenceTransformer

warnings.filterwarnings("ignore")

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model():
    # Lazy loading keeps FastAPI startup lightweight and avoids resolving the
    # embedding model until retrieval is actually needed.
    return SentenceTransformer(MODEL_NAME)


def get_embeddings(texts):
    """
    Returns a list of vectors for the given text chunks.
    """
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


def get_query_embedding(query):
    model = _get_model()
    return model.encode(query, show_progress_bar=False).tolist()
