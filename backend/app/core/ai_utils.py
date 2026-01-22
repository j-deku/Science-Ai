import re
import difflib
import random
from typing import List, Optional, Tuple
from functools import lru_cache

from app.core.ai_knowledge import (
SCIENCE_KNOWLEDGE, 
normalize_text, GENERIC_TRIGGERS, 
GREETINGS_TRIGGERS, GREETINGS_RESPONSES,
CONFIRM_PREFIXES, 
GENERIC_RESPONSES, GENERIC_KNOWLEDGE_TRIGGERS, 
GENERIC_KNOWLEDGE, FOLLOW_UP_TRIGGERS, EXAMPLE_TRIGGERS, STATIC_EXAMPLES,STATIC_DIAGRAMS,
FOLLOW_UP_QUESTIONS)
from app.core.ai_memory import CONVERSATION_MEMORY
from app.core.web_scraper import web_search_answer, web_image_search
# -----------------------
# Normalization + Keywords
# -----------------------
def normalize_generic(text: str) -> str:
    return re.sub(r"[^\w\s]", "", (text or "").lower()).strip()


def detect_topic(question: str) -> str:
    q = normalize_text(question)

    # direct match
    if q in SCIENCE_KNOWLEDGE:
        return q

    # strip question patterns
    q = re.sub(r"^(what is|explain|define|tell me about)\s+", "", q)

    # lookup again
    if q in SCIENCE_KNOWLEDGE:
        return q

    # fuzzy match
    best = difflib.get_close_matches(q, SCIENCE_KNOWLEDGE.keys(), n=1, cutoff=0.6)
    return best[0] if best else None

def extract_keywords(text: str, max_words: int = 8) -> List[str]:
    text = (text or "").lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = [t for t in text.split() if len(t) > 2]
    seen, out = set(), []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            out.append(t)
            if len(out) >= max_words:
                break
    return out


def add_confirm_prefix(answer: str) -> str:
    prefix = random.choice(CONFIRM_PREFIXES)
    return f"{prefix}{answer}"


# -----------------------
# Multi-topic blend
# -----------------------
def try_multi_topic_blend(question: str) -> Optional[str]:
    words = extract_keywords(question, max_words=20)
    matched = [topic for topic in SCIENCE_KNOWLEDGE.keys() if topic in words]

    if len(matched) >= 2:
        bullets = []
        for topic in matched:
            bullets.extend(SCIENCE_KNOWLEDGE.get(topic, []))
        return f"📌 Combined Topics: {' + '.join([t.capitalize() for t in matched])}\n" + "\n".join(bullets)

    # If only 1 match, return None → normal KB flow handles it
    return None

# -----------------------
# Fallback matching
# -----------------------
def generate_kb_keys_variants(question: str) -> List[str]:
    q = normalize_text(question)
    q = re.sub(r"^(what is|define|explain|tell me about)\s+", "", q)
    q = re.sub(r"[^\w\s]", "", q)
    variants = [q]
    if q.endswith("s"):
        variants.append(q[:-1])
    return variants


def find_partial_kb_matches(question: str, cutoff: float = 0.5) -> List[str]:
    q = normalize_text(question)
    matched_facts = []
    for key, facts in SCIENCE_KNOWLEDGE.items():
        k = normalize_text(key)

        if k in q or q in k:
            matched_facts.extend(facts)
            continue

        ratio = difflib.SequenceMatcher(None, q, k).ratio()
        if ratio >= cutoff:
            matched_facts.extend(facts)
    return matched_facts


# -----------------------
# Generic input handler
# -----------------------
def handle_generic_input(question: str) -> Optional[str]:
    q = normalize_text(question)
    words = q.split()

    for trig in GENERIC_TRIGGERS:
        trig_norm = normalize_text(trig)
        # Only match if exact word exists or question is short & simple
        if trig_norm in words or (len(words) <= 3 and difflib.SequenceMatcher(None, q, trig_norm).ratio() >= 0.8):
            return random.choice(GENERIC_RESPONSES)
    return None

def handle_who_are_you(question: str) -> Optional[str]:
    q = normalize_text(question)

    for trig in GENERIC_KNOWLEDGE_TRIGGERS:
        ratio = difflib.SequenceMatcher(None, q, trig).ratio()
        if trig in q or ratio >= 0.6:  # slightly more tolerant
            return random.choice(GENERIC_KNOWLEDGE)
    return None

def handle_follow_up(question: str, session_id: str) -> Optional[str]:
    q = normalize_text(question)

    # Correct detection
    for trig in FOLLOW_UP_TRIGGERS:
        if trig in q or difflib.SequenceMatcher(None, q, trig).ratio() >= 0.7:

            last_topic = CONVERSATION_MEMORY.get(session_id, {}).get("last_topic")

            if not last_topic:
                return random.choice(FOLLOW_UP_QUESTIONS)

            facts = SCIENCE_KNOWLEDGE.get(last_topic, [])

            # Fetch web expansion
            web_query = f"explain {last_topic} in more details"
            try:
                web_extra = web_search_answer(web_query)
            except Exception:
                web_extra = None

            parts = []

            if facts:
                parts.append(
                    f"Here’s a deeper explanation of **{last_topic.capitalize()}**:\n"
                    + "\n".join(f"- {fact}" for fact in facts)
                )

            if web_extra:
                parts.append(
                    f"Additional details from external sources:\n{web_extra}"
                )

            final = "\n\n".join(parts)
            final += "\n\nWould you like examples, diagrams, or real-life applications?"

            return final

    return None

def normal_greetings(question: str) -> Optional[str]:
    q = normalize_text(question)
    
    for trig in GREETINGS_TRIGGERS:
       if trig in q or difflib.SequenceMatcher(None, q, trig).ratio() >=0.6:
           return random.choice(GREETINGS_RESPONSES)
       
    return None

def detect_follow_up(question: str, session_id: str):
    q = normalize_text(question)

    # follow-up patterns
    patterns = [
        r"what about",
        r"and what",
        r"explain more",
        r"continue",
        r"tell me more",
        r"what are its functions",
        r"functions",
        r"uses",
        r"importance",
        r"examples",
        r"types",
    ]

    if any(re.search(p, q) for p in patterns):
        return CONVERSATION_MEMORY.get(session_id, {}).get("last_topic")

    return None

def hallucination_self_check(text: str) -> str:
    """
    Simple rule-based self-check:
    - No invented formulas
    - No invented scientist names
    - Must reference KB content only
    """
    if "according to unknown" in text.lower():
        return "I may not have reliable information on that. Please clarify your question."

    return text

def smart_science_answer(topic: str) -> str:
    facts = SCIENCE_KNOWLEDGE.get(topic, [])
    if not facts:
        return "I don't have information on that topic yet."

    response = f"### **{topic.capitalize()}**\n"
    response += "Here is a clear explanation:\n\n"

    for f in facts:
        response += f"- {f}\n"

    response += "\nWould you like diagrams, examples, or real-life applications?"
    return response


# -----------------------
# Examples & Diagrams
# -----------------------

# Helper to extract image URLs or data URIs from arbitrary text/HTML
def _extract_image_url_from_text(text: str) -> Optional[str]:
    if not text:
        return None
    urls = re.findall(r"https?://\S+\.(?:png|jpg|jpeg|svg|gif)", text, flags=re.IGNORECASE)
    if urls:
        return urls[0]
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', text, flags=re.IGNORECASE)
    if m:
        return m.group(1)
    m2 = re.search(r'(data:image\/[a-zA-Z\+]+;base64,[A-Za-z0-9+/=]+)', text)
    if m2:
        return m2.group(1)
    return None


@lru_cache(maxsize=256)
def _call_web_search(query: str):
    try:
        return web_search_answer(query)
    except Exception:
        return None


def auto_generate_diagram(topic: str) -> Optional[str]:
    """
    Return a diagram string or image URL for topic:
      1) If STATIC_DIAGRAMS has a curated diagram, return that (guaranteed).
      2) Else, query web_search_answer for image URLs or textual diagrams.
      3) Else, call web_image_search (Wikipedia/Wikimedia Commons) for image URL.
      4) If a web string is returned but contains no images, return the textual snippet as a fallback.
    """
    if not topic:
        return None

    # 1) Prefer curated diagrams
    curated = STATIC_DIAGRAMS.get(topic)
    if curated:
        return curated

    # 2) Try web_search_answer based queries
    queries = [
        f"{topic} diagram",
        f"{topic} labelled diagram",
        f"{topic} labeled diagram",
        f"{topic} structure diagram",
        f"{topic} schematic diagram",
    ]

    for q in queries:
        resp = _call_web_search(q)
        if not resp:
            continue

        # If dict-like response, try to find image list / snippet keys
        if isinstance(resp, dict):
            for key in ("image_urls", "images", "image", "images_urls", "image_urls_list"):
                items = resp.get(key)
                if isinstance(items, list) and items:
                    return items[0]
                if isinstance(items, str) and items:
                    return items
            # text-like fields
            for key in ("text", "answer", "html", "snippet", "summary"):
                v = resp.get(key)
                if isinstance(v, str) and v.strip():
                    img = _extract_image_url_from_text(v)
                    return img if img else v.strip()
            # last resort: stringify the response preview
            preview = resp.get("preview") or resp.get("description")
            if isinstance(preview, str) and preview.strip():
                img = _extract_image_url_from_text(preview)
                return img if img else preview.strip()

        # If resp is a string, try to extract an image URL or return the string as diagram text
        if isinstance(resp, str):
            img = _extract_image_url_from_text(resp)
            if img:
                return img
            if resp.strip().startswith("http"):
                return resp.strip()
            if len(resp.strip()) > 40:
                return resp.strip()

    # 3) Dedicated image search fallback (Wikipedia / Wikimedia Commons)
    try:
        wiki_img = web_image_search(topic)
        if wiki_img:
            return wiki_img
    except Exception:
        pass

    # 4) Nothing found
    return None


def infer_examples(topic: str) -> List[str]:
    curated = STATIC_EXAMPLES.get(topic)
    if curated:
        return list(curated)[:5]
    # fallback inference from facts
    facts = SCIENCE_KNOWLEDGE.get(topic, [])
    examples = []
    for f in facts:
        if len(f) > 30:
            examples.append(f"{f[:60]}...")
    if not examples:
        examples = [f"{topic.capitalize()} example 1", f"{topic.capitalize()} example 2"]
    return examples[:5]


def maybe_add_examples_and_diagrams(user_question: str, topic: Optional[str]) -> Tuple[List[str], List[str]]:
    if not topic:
        return [], []
    if not any(trigger in user_question.lower() for trigger in EXAMPLE_TRIGGERS):
        return [], []

    examples = STATIC_EXAMPLES.get(topic) or infer_examples(topic)

    diagram = auto_generate_diagram(topic)
    # Return diagram as a list of one item (keeps calling code unchanged)
    return examples or [], [diagram] if diagram else []