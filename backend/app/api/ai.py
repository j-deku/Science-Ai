# app/api/ai.py
from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse
import uuid
import json
from gtts import gTTS
import speech_recognition as sr
import uuid
from typing import List, Dict, Any

from app.core.ai_integration import answer_science_question_sync, answer_science_question_stream
from app.core.embedding_loader import add_documents, get_collection

router = APIRouter(prefix="/ai", tags=["AI"])

class QuestionRequest(BaseModel):
    question: str
    session_id: str = None
    top_k: int = 6

class SourceModel(BaseModel):
    topic: str
    preview: str
    distance: float
    score: float

class AnswerResponse(BaseModel):
    answer: str
    sources: List[SourceModel] = []
    explanation: List[str] = []

@router.post("/ask_sync", response_model=AnswerResponse)
def ask_sync(req: QuestionRequest):
    session_id = req.session_id or str(uuid.uuid4())
    ret = answer_science_question_sync(req.question, session_id=session_id, top_k=req.top_k)
    # ensure types are serializable
    return JSONResponse({
        "answer": ret.get("answer", ""),
        "sources": ret.get("sources", []),
        "explanation": ret.get("explanation", [])
    })

@router.post("/ai/stream")
async def ai_stream(request: Request):
    body = await request.json()
    question = body.get("question")
    session_id = body.get("session_id") or str(uuid.uuid4())

    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    def event_generator():
        # Step 1: initial status
        yield "data: [status] Searching knowledge base... 🔍\n\n"

        # Step 2: stream AI answer chunk by chunk
        for chunk in answer_science_question_stream(question, session_id=session_id, top_k=6):
            yield f"data: {chunk}\n\n"

        # Step 3: final web search / completion status
        yield "data: [status] Web search completed 🌐\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Admin endpoints remain the same
class AddKnowledgeRequest(BaseModel):
    topic: str
    facts: List[str]

@router.post("/knowledge/add")
def add_knowledge(payload: AddKnowledgeRequest):
    docs = [{"id": str(uuid.uuid4()), "topic": payload.topic, "text": fact} for fact in payload.facts]
    res = add_documents(docs)
    return {"status": "ok", "added": res.get("added", 0)}

@router.post("/knowledge/upload_json")
async def upload_json(file: UploadFile = File(...)):
    raw = await file.read()
    try:
        data = json.loads(raw)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")

    docs = []
    for item in data:
        topic = item.get("topic")
        facts = item.get("facts", [])
        for f in facts:
            docs.append({"id": str(uuid.uuid4()), "topic": topic, "text": f})
    res = add_documents(docs)
    return {"status": "ok", "added": res.get("added", 0)}

@router.get("/knowledge/list")
def list_topics():
    collection = get_collection()
    try:
        results = collection.get(include=["metadatas"])
        topics = {m.get("topic") for m in results.get("metadatas", []) if m.get("topic")}
        return {"topics": sorted(topics)}
    except Exception:
        return {"topics": []}

@router.post("/ai/speech-to-text")
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.AudioFile("user_audio.wav") as source:
        audio = recognizer.record(source)

    text = recognizer.recognize_google(audio)
    return {"text": text}

@router.post("/ai/text-to-speech")
def text_to_speech(data: dict):
    filename = f"tts_{uuid.uuid4()}.mp3"
    gTTS(data["text"]).save(filename)
    return {"speech_file": filename}
