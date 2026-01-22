# app/core/ai_retrieval.py

import re
from typing import List, Dict
from app.core.ai_utils import extract_keywords

def combine_unique_texts(texts: List[str], max_chars: int = 2000) -> str:
    if not texts:
        return ""
    seen, sentences = set(), []
    for doc in texts:
        for s in re.split(r'(?<=[.!?])\s+', doc.strip()):
            clean = s.strip()
            if not clean:
                continue
            key = clean.lower()
            if key in seen:
                continue
            seen.add(key)
            sentences.append(clean)
            if sum(len(x) for x in sentences) > max_chars:
                break
    return " ".join(sentences).strip()

def rerank_candidates(question: str, docs: List[str], metas: List[dict], distances: List[float]):
    keywords = set(extract_keywords(question))
    candidates = []

    for text, meta, dist in zip(docs, metas, distances):
        nd = min(1.0, max(0.0, float(dist or 1.0)))
        words = set(re.findall(r"\w+", (text or "").lower()))
        kw_score = len(words & keywords) / max(1, len(keywords)) if keywords else 0.0

        score = 0.6 * (1 - nd) + 0.4 * kw_score

        candidates.append({
            "text": text,
            "metadata": meta or {},
            "distance": nd,
            "score": round(score, 4)
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates
