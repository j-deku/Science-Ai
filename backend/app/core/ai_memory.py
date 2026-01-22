from typing import Dict, List, Any

# Conversation memory now stores BOTH:
# - message history
# - learned topics
CONVERSATION_MEMORY: Dict[str, Any] = {}


def remember(session_id: str, role: str, content: str, max_turns: int = 10):
    if session_id not in CONVERSATION_MEMORY:
        CONVERSATION_MEMORY[session_id] = {
            "messages": [],
            "learned_topics": set()
        }

    # Store only messages inside messages[]
    CONVERSATION_MEMORY[session_id]["messages"].append({
        "role": role,
        "content": content
    })

    # Trim message memory
    msgs = CONVERSATION_MEMORY[session_id]["messages"]
    CONVERSATION_MEMORY[session_id]["messages"] = msgs[-max_turns:]


def get_recent_user_context(session_id: str, limit: int = 3) -> str:
    if session_id not in CONVERSATION_MEMORY:
        return ""

    history = CONVERSATION_MEMORY[session_id]["messages"]
    user_msgs = [m["content"] for m in history if m["role"] == "user"]

    if not user_msgs:
        return ""

    return " | ".join(user_msgs[-limit:])
