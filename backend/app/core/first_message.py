# app/core/first_message.py

import difflib, random
from app.core.ai_knowledge import FIRST_MESSAGE_TRIGGERS, GENERIC_TRIGGERS, CLARIFICATION_QUESTIONS
from app.core.ai_knowledge import normalize_text
from app.core.ai_memory import remember, CONVERSATION_MEMORY

def handle_first_message(question: str, session_id: str):
    history = CONVERSATION_MEMORY.get(session_id, [])
    user_messages = [m for m in history if m["role"] == "user"]

    # Only trigger on the VERY first message
    if len(user_messages) != 1:
        return None

    normalized = normalize_text(question)

    for trigger in FIRST_MESSAGE_TRIGGERS + GENERIC_TRIGGERS:
        ratio = difflib.SequenceMatcher(None, normalized, trigger).ratio()
        if ratio >= 0.7:
            reply = random.choice(CLARIFICATION_QUESTIONS)
            remember(session_id, "assistant", reply)
            return reply

    return None
