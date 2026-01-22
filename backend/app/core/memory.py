SESSION_MEMORY = {}

def remember(session_id: str, user_question: str, ai_answer: str):
    SESSION_MEMORY.setdefault(session_id, []).append({
        "q": user_question,
        "a": ai_answer
    })

def get_history(session_id: str):
    return SESSION_MEMORY.get(session_id, [])
