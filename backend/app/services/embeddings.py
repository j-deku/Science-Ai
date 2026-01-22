from sentence_transformers import SentenceTransformer
from app.core.config import EMBEDDING_MODEL


# load model once
embedding_model = SentenceTransformer(EMBEDDING_MODEL)




def embed_text(text: str):
    vec = embedding_model.encode(text)
    return vec.tolist() if hasattr(vec, 'tolist') else list(vec)