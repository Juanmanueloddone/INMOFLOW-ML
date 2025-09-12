# ml/embeddings.py
import os
from functools import lru_cache
import numpy as np
from openai import OpenAI

MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def _embed_once(text: str) -> np.ndarray:
    r = _client.embeddings.create(model=MODEL, input=text)
    return np.array(r.data[0].embedding, dtype=np.float32)

@lru_cache(maxsize=2048)
def embed_cached(text: str) -> np.ndarray:
    # caché en memoria (efectivo para requests repetidos)
    return _embed_once(text)

def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom else 0.0
