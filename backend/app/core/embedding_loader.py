from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os

from app.core.config import CHROMA_PERSIST_DIR, EMBEDDING_MODEL

# Initialize SentenceTransformer
model = SentenceTransformer(EMBEDDING_MODEL)

# --- NEW CHROMA CLIENT (v0.4+) ---
client = Client(
    Settings(
        chroma_db_impl="duckdb+parquet",  # storage backend
        persist_directory=CHROMA_PERSIST_DIR,
        anonymized_telemetry=False       # optional
    )
)

def get_collection(name="science_knowledge"):
    # Chroma v0.4+ list_collections() returns Collection objects
    existing_collections = [c.name for c in client.list_collections()]
    if name not in existing_collections:
        client.create_collection(name=name)
    return client.get_collection(name)

def embed_texts(texts):
    return model.encode(texts, show_progress_bar=False).tolist()

def add_documents(docs):
    """
    docs: List[{"id": str, "topic": str, "text": str}]
    """
    collection = get_collection()
    ids = [d["id"] for d in docs]
    metadatas = [{"topic": d["topic"]} for d in docs]
    texts = [d["text"] for d in docs]
    embeddings = embed_texts(texts)

    collection.add(
        documents=texts,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings
    )
    client.persist()
    return {"added": len(docs)}

def query_similar(query, top_k=3):
    collection = get_collection()
    emb = embed_texts([query])[0]
    results = collection.query(
        query_embeddings=[emb],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    return results
