# Simple AI integration placeholder. Replace with your preferred model logic.
from typing import List
from app.services.embeddings import embed_text




def answer_question(question: str, top_contexts: List[str] | None = None) -> str:
    # naive response — in production you'd query a vector DB, fetch contexts, and run a generative model
    ctx = "\n\n".join(top_contexts or [])
    return f"Answer to: {question}\n\nRelevant context:\n{ctx[:2000]}"