# app/core/ai_core.py

import random
import difflib
from typing import Any, Dict, List, Tuple

from app.core.ai_memory import remember, get_recent_user_context, CONVERSATION_MEMORY
from app.core.ai_utils import (
    handle_generic_input, try_multi_topic_blend, add_confirm_prefix,
    generate_kb_keys_variants, find_partial_kb_matches, 
    detect_topic, extract_keywords, handle_who_are_you, 
    handle_follow_up, normal_greetings, maybe_add_examples_and_diagrams,
    smart_science_answer, detect_follow_up, infer_examples, auto_generate_diagram
)
from app.core.ai_retrieval import rerank_candidates, combine_unique_texts

from app.core.embedding_loader import query_similar
from app.core.ai_knowledge import SCIENCE_KNOWLEDGE, normalize_text, FIRST_MESSAGE_TRIGGERS, CLARIFICATION_QUESTIONS, GENERIC_TRIGGERS, REPEAT_TOPIC_PREFIXES
from app.core.web_scraper import web_search_answer
from app.core.learning_memory import record_unknown_question
from app.core.guardrails import hallucination_blocker

# =====================================================
# MAIN SYNTHESIS FUNCTION
# =====================================================
def synthesize_answer(question: str, candidates: List[dict], session_id: str):
    explanation = []
    used_sources = []

    normalized_question = normalize_text(question)
    
    # =====================================================
    # 4. STRICT topic detection (improved) + examples/diagrams
    # =====================================================
    topic = detect_topic(question)
    if topic:
        facts = SCIENCE_KNOWLEDGE.get(topic, [])
        learned_topics = CONVERSATION_MEMORY.get(session_id, {}).get("learned_topics", set())
        CONVERSATION_MEMORY.setdefault(session_id, {})["last_topic"] = topic

        # Compose main answer
        if topic in learned_topics:
            prefix = random.choice(REPEAT_TOPIC_PREFIXES)
            answer = prefix + " ".join(facts)
        else:
            answer = " ".join(facts)
            learned_topics.add(topic)
            CONVERSATION_MEMORY[session_id]["learned_topics"] = learned_topics

        # --- Add examples/diagrams only if user requested ---
        EXAMPLE_TRIGGERS = [
            "i need examples",
            "explain with diagrams",
            "explain further",
            "give examples",
            "show diagram",
            "more details",
            "illustrate"
        ]
        if any(trigger in question.lower() for trigger in EXAMPLE_TRIGGERS):
            examples, diagrams = maybe_add_examples_and_diagrams(question, topic)
            if examples:
                answer += "\n\n**Examples:**\n" + "\n".join(f"- {e}" for e in examples)
            if diagrams:
                answer += "\n\n**Diagram:**\n" + "\n".join(diagrams)

        return answer, [], [f"Topic detected: {topic}"]
    # =====================================================
    # 0. Handle greetings early (important)
    # =====================================================
    greetings = normal_greetings(question)
    if greetings:
        return greetings, [], ["Greeting detected."]

    # =====================================================
    # 1. Strong generic handler (who are you / simple inputs)
    # =====================================================
    generic = handle_generic_input(question)
    if generic:
        return generic, [], ["Generic response."]

    who = handle_who_are_you(question)
    if who:
        return who, [], ["'Who are you' style response."]

    # =====================================================
    # 2. Smart follow-up handling
    # =====================================================
    follow_up = handle_follow_up(question, session_id)
    if follow_up:
        return follow_up, [], ["Follow-up handled."]

        # =====================================================
    # 2b. Check if user requested examples/diagrams
    # =====================================================
    EXAMPLE_TRIGGERS = [
        "i need examples",
        "explain with diagrams",
        "explain further",
        "give examples",
        "show diagram",
        "more details",
        "illustrate"
    ]

    normalized_lower = normalized_question.lower()
    if any(trigger in normalized_lower for trigger in EXAMPLE_TRIGGERS):
        # Determine last topic from memory
        last_topic = CONVERSATION_MEMORY.get(session_id, {}).get("last_topic")
        if last_topic:
            examples = infer_examples(last_topic)
            diagram = auto_generate_diagram(last_topic)
            answer_parts = []

            if examples:
                answer_parts.append("**Examples:**\n" + "\n".join(f"- {e}" for e in examples))
            if diagram:
                answer_parts.append(f"**Diagram:**\n{diagram}")

            if answer_parts:
                answer_text = "\n\n".join(answer_parts)
                return answer_text, [], [f"Examples/Diagram for topic: {last_topic}"]

    # =====================================================
    # 3. Multi-topic blend
    # =====================================================
    blend = try_multi_topic_blend(question)
    if blend:
        return blend, [], ["Multi-topic blend provided."]

    # =====================================================
    # 5. Retrieval candidates (embeddings)
    # =====================================================
    selected = []
    seen_topics = set()

    for c in candidates:
        meta_topic = (c.get("metadata") or {}).get("topic", "")
        if meta_topic in seen_topics:
            continue

        seen_topics.add(meta_topic)
        selected.append(c["text"])
        used_sources.append({
            "topic": meta_topic,
            "preview": c["text"][:150],
            "score": c.get("score")
        })

        if len(selected) >= 3:
            break

    if selected:
        combined = combine_unique_texts(selected)
        return combined, used_sources, ["Retrieved from embedding DB."]

    # =====================================================
    # 6. NEW: Partial KB matching BEFORE web search
    # =====================================================
    partial = find_partial_kb_matches(question)
    if partial:
        return " ".join(partial), [], ["Partial KB match triggered."]

    # =====================================================
    # 7. Web search fallback
    # =====================================================
    web_result = web_search_answer(question)
    if web_result:
        return web_result, [], ["Web search used."]

    # =====================================================
    # 8. Loose keyword fallback (last KB rescue)
    # =====================================================
    kws = extract_keywords(question)
    for w in kws:
        for key in SCIENCE_KNOWLEDGE:
            if w in key or key in w:
                facts = SCIENCE_KNOWLEDGE[key]
                return " ".join(facts), [], ["Loose keyword fallback."]

    # =====================================================
    # 9. Unknown → learning memory
    # =====================================================
    record_unknown_question(question)
    suggestions = ", ".join(list(SCIENCE_KNOWLEDGE.keys())[:5])
    return f"I don’t know that yet. Try: {suggestions}", [], ["Unknown query fallback."]

# =====================================================
# PUBLIC API — SYNC
# =====================================================

def answer_science_question_sync(question: str, session_id: str, top_k: int = 6):
    # -------------------------------
    # Store user message
    # -------------------------------
    remember(session_id, "user", question)

    # -------------------------------
    # First-message clarification
    # -------------------------------
    history = CONVERSATION_MEMORY.get(session_id, {}).get("messages", [])
    first_user_msgs = [m for m in history if m["role"] == "user"]

    if len(first_user_msgs) == 1:
        normalized = normalize_text(question)
        for generic_trigger in GENERIC_TRIGGERS + FIRST_MESSAGE_TRIGGERS:
            if difflib.SequenceMatcher(None, normalized, generic_trigger).ratio() >= 0.7:
                resp = random.choice(CLARIFICATION_QUESTIONS)
                remember(session_id, "assistant", resp)
                return {"answer": resp, "sources": [], "explanation": ["First-message clarification."]}

    # -------------------------------
    # Context-aware retrieval
    # -------------------------------
    recent = get_recent_user_context(session_id)
    context_query = f"{recent} | {question}" if recent else question

    results = query_similar(context_query, top_k=top_k)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    candidates = rerank_candidates(question, docs, metas, dists)

    # -------------------------------
    # Synthesize final answer
    # -------------------------------
    answer_text, used_sources, steps = synthesize_answer(question, candidates, session_id)

    remember(session_id, "assistant", answer_text)

    return {
        "answer": answer_text,
        "sources": used_sources,
        "explanation": steps
    }

def generate_response(question: str, session_id: str):
    q = normalize_text(question)

    # 1️⃣ try to detect topic FIRST
    topic = detect_topic(q)
    if topic:
        CONVERSATION_MEMORY.setdefault(session_id, {})["last_topic"] = topic
        return smart_science_answer(topic)
    
        # FOLLOW-UP DETECTION
    follow_topic = detect_follow_up(q, session_id)
    if follow_topic:
       # If the user is following up (e.g. "i need examples", "show diagram"),
        # attempt to include examples and/or diagrams automatically.
        examples, diagrams = maybe_add_examples_and_diagrams(question, follow_topic)

        # Compose a response that includes the standard explanation plus
        # the requested examples/diagrams when available.
        main = smart_science_answer(follow_topic)

        if examples or diagrams:
            parts = [main]
            if examples:
                parts.append("**Examples:**\n" + "\n".join(f"- {e}" for e in examples))
            if diagrams:
                parts.append("**Diagram:**\n" + "\n".join(diagrams))
            return "\n\n".join(parts)

        # Fallback: return the normal explanation if no examples/diagrams found
        return main

    # 2️⃣ greetings (if no topic found)
    greet = normal_greetings(q)
    if greet:
        return greet

    # 3️⃣ generic inputs
    gen = handle_generic_input(q)
    if gen:
        return gen

    # 4️⃣ who are you
    who = handle_who_are_you(q)
    if who:
        return who

    # 5️⃣ follow-up logic
    follow = handle_follow_up(q, session_id)
    if follow:
        return follow

    # 6️⃣ fallback KB search
    facts = find_partial_kb_matches(q)
    if facts:
        return "Here’s what I found based on your question:\n" + "\n".join("- " + f for f in facts)

    # 7️⃣ last fallback
    return "I’m not sure I understand. Can you rephrase your science question?"

# =====================================================
# STREAMING API
# =====================================================
def answer_science_question_stream(question: str, session_id: str, top_k: int = 6):
    yield "[status] Searching the web... 🔍\n"

    result = answer_science_question_sync(question, session_id, top_k)

    yield "[status] Retrieved knowledge base results ✅\n"

    text = result["answer"]
    chunk_size = 80

    for i in range(0, len(text), chunk_size):
        yield text[i:i+chunk_size]

    yield "[status] Done 🟢\n"
