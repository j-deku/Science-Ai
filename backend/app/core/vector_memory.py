# app/core/vector_memory.py
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.config import EMBEDDING_MODEL

model = SentenceTransformer(EMBEDDING_MODEL)


# Simple in-memory vector store
# session_id -> List of (embedding, text)
VECTOR_MEMORY = {}

def embed_text(text: str) -> np.ndarray:
    return model.encode([text])[0]

def add_to_memory(session_id: str, text: str):
    emb = embed_text(text)
    VECTOR_MEMORY.setdefault(session_id, []).append((emb, text))

def retrieve_context(session_id: str, question: str, top_k: int = 3) -> List[str]:
    if session_id not in VECTOR_MEMORY:
        return []

    query_emb = embed_text(question)
    all_embs, texts = zip(*VECTOR_MEMORY[session_id])
    sims = cosine_similarity([query_emb], all_embs)[0]
    # Get top_k most similar texts
    top_indices = sims.argsort()[-top_k:][::-1]
    return [texts[i] for i in top_indices]
