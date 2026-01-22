from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List
from app.core.embedding_loader import add_documents
from app.core.ai_knowledge import SCIENCE_KNOWLEDGE
from app.core.learning_memory import mark_question_learned
from app.core.local_embedder import embed_and_store

router = APIRouter(prefix="/ai/admin", tags=["AI"])

class TeachSchema(BaseModel):
    topic: str
    facts: List[str]
@router.post("/ai/admin/teach")
def teach_ai(data: TeachSchema):
    embed_and_store(data.topic, data.facts)
    mark_question_learned(data.topic)
    return {"status": "updated", "topic": data.topic}
