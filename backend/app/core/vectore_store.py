# app/core/vector_store.py
import os
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

EMBED_MODEL = None

def get_embedder():
    global EMBED_MODEL
    if EMBED_MODEL is None:
        EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return EMBED_MODEL

class FaissStore:
    def __init__(self, dim=384, index_path="data/faiss.index", meta_path="data/faiss_meta.json"):
        self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []
        # load if exists
        if Path(index_path).exists():
            self.index = faiss.read_index(index_path)
            if Path(meta_path).exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)

    def add(self, texts: list, metas: list):
        em = get_embedder()
        vectors = em.encode(texts)
        self.index.add(np.array(vectors).astype("float32"))
        self.metadata.extend(metas)
        self._persist()

    def query(self, qtext: str, top_k: int = 5):
        em = get_embedder()
        qv = em.encode([qtext]).astype("float32")
        D, I = self.index.search(qv, top_k)
        results = []
        for idx, dist in zip(I[0], D[0]):
            if idx < len(self.metadata):
                results.append({"metadata": self.metadata[idx], "score": float(dist)})
        return results

    def _persist(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
