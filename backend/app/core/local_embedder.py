from sentence_transformers import SentenceTransformer
import json, os

EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")  # fast + small

def embed_and_store(topic: str, facts: list):
    embedding_dir = "vector_memory"
    os.makedirs(embedding_dir, exist_ok=True)

    vectors = EMBEDDER.encode(facts).tolist()

    with open(f"{embedding_dir}/{topic}.json", "w") as f:
        json.dump({"topic": topic, "facts": facts, "vectors": vectors}, f)
