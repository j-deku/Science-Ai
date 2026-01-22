# app/core/ai_knowledge.py
"""
Central Knowledge Base (KB)
---------------------------
This module should contain ONLY static knowledge + utilities.
No file writing.
No DB writing.
No learning logic.
No side-effects at import time.

All learning/memory is handled by learning_memory.py.
All vector search is handled by vector_store.py.

This file defines the static Integrated Science knowledge and helper
functions to retrieve it safely.
"""

from typing import Dict, List, Optional

# ------------------------------
# STATIC SCIENCE KNOWLEDGE BASE
# ------------------------------
# NOTE: This is your syllabus knowledge. Expand at any time.
#       This is NOT dynamically modified at runtime.
import random
import re
from app.core.learning_memory import mark_question_learned
SCIENCE_KNOWLEDGE: Dict[str, List[str]] = {
    "science": [
        "Science is the systematic study of the natural world.",
        "It involves observation, experimentation, and drawing conclusions.",
        "Science helps us understand matter, energy, living things, and the environment."
    ],
    "cell": [
        "A cell is the basic structural and functional unit of life.",
        "All living organisms are made of one or more cells.",
        "Cells carry out processes like respiration, growth, and reproduction."
    ],
    "matter": [
        "Matter is anything that has mass and occupies space.",
        "States of matter include solid, liquid, and gas.",
        "Matter is made up of tiny particles called atoms and molecules."
    ],
    "energy": [
        "Energy is the ability to do work.",
        "Common forms include heat, light, sound, electrical, and kinetic energy.",
        "Energy can neither be created nor destroyed, only transformed."
    ],
}
EXAMPLE_TRIGGERS = [
    "i need examples",
    "give examples",
    "explain with examples",
    "explain further",
    "explain with diagrams",
    "show diagram",
    "illustrate",
    "examples please"
]
# -------------------------------
# Static examples dictionary
# -------------------------------
STATIC_EXAMPLES = {
    "energy": [
        "Heat energy (e.g., boiling water)",
        "Light energy (e.g., sunlight)",
        "Sound energy (e.g., a ringing bell)",
        "Chemical energy (e.g., energy in food or batteries)",
        "Kinetic energy (e.g., a moving car)"
    ],
    "cell": [
        "Plant cell — e.g., a mesophyll (leaf) cell with chloroplasts for photosynthesis",
        "Animal cell — e.g., a muscle cell specialized for contraction",
        "Bacterial (prokaryotic) cell — a single-celled organism without a nucleus",
        "Yeast cell — a unicellular fungus used in baking and fermentation",
        "Neuron — a specialized nerve cell that transmits signals"
    ],
    "force": [
        "Frictional force — opposes motion between surfaces",
        "Gravitational force — pulls objects toward one another",
        "Magnetic force — acts between magnets or magnetic materials"
    ],
    "matter": [
        "Solid — e.g., ice, wood",
        "Liquid — e.g., water, oil",
        "Gas — e.g., oxygen, carbon dioxide"
    ]
}

# Curated diagrams: prefer these first (textual/markdown diagrams or image URLs).
# Keep entries short, human-readable, and educational.
STATIC_DIAGRAMS = {
    "cell": (
        "Simple labelled plant cell (text diagram):\n\n"
        "  +-------------------------------+\n"
        "  |        Plant Cell             |\n"
        "  |  +-----------+   +---------+  |\n"
        "  |  | Nucleus   |   | Chlor-  |  |\n"
        "  |  | (control) |   | oplast  |  |\n"
        "  |  +-----------+   +---------+  |\n"
        "  |  (cell wall) [rigid outer layer]\n"
        "  |  (cell membrane) [controls entry/exit]\n"
        "  |  (vacuole) [storage]\n"
        "  +-------------------------------+\n\n"
        "Labels: Nucleus, Chloroplast, Cell wall, Cell membrane, Vacuole\n"
        "Use this as a quick reference; for an image, ask 'show an image of a plant cell'."
    ),
    "energy": (
        "Energy diagram (concept map):\n\n"
        "- Sources: Sunlight → Light energy\n"
        "- Transformations: Chemical energy (food) → Kinetic energy (movement)\n"
        "- Examples: Heat (friction), Light (bulb), Sound (speaker)\n\n"
        "This is a conceptual diagram. For a pictorial diagram, ask 'show an image of energy forms'."
    ),
    # Add more curated diagram entries as needed.
}

GREETINGS_TRIGGERS = [ "hello", "whatsupp", "whatsApp", "wassup", "wossup", "hi", "hii" ]
GREETINGS_RESPONSES = [
    "Hello! How are you doing today?😊",
    "Hi! How are you doing?",
    "Yeah, how are you doing today? Anything for me?",
    "Yo charley! i dey cool ooo your syd?😊",
    ]
# Generic input triggers (normalized)
GENERIC_TRIGGERS = [
    "thanks", "thank you", "ok", "okay", "thx", "thnks", "ty", "thanks a lot", "thank u", "got it", "understood",
    "cool", "great", "awesome", "nice", "good job", "well done", "appreciate it", "cheers", "well appreciated",
]
# Friendly responses for generic inputs
GENERIC_RESPONSES = [
    "You're welcome! 😊",
    "No problem! 😄",
    "Glad to help! 👍",
    "Anytime! 🙂",
    "Happy to assist! 🤗",
    "Sure thing! 😃",
    "My pleasure! 😎"
]


GENERIC_KNOWLEDGE_TRIGGERS = [
    "who are you", "what is your name", "introduce yourself", "tell me about yourself",
    "what's your name",
]
GENERIC_KNOWLEDGE = [
    "I am your Integrated Science AI assistant 🤖. \n Do you have any question related to science?",
    "My name is CeXo and i'm here to assist you in Integrated Science. Do you have any questions?",
    "I'm an AI developed to help you with Integrated Science topics. What would you like to know?",
    "Hello! I'm your Integrated Science AI helper. Feel free to ask me anything about science!",
    "I'm CeXo, your go-to AI for Integrated Science questions. How can I assist you today?",
    "Hi! I'm an AI assistant specialized in Integrated Science. What science topic are you curious about?",
    "Greetings! I'm here to help you with Integrated Science. What would you like to learn today?",
    "I'm your Integrated Science AI companion. Ask me anything related to science!",
    "Hey there! I'm an AI focused on Integrated Science. What science questions do you have?",
    "I'm CeXo, your Integrated Science AI guide. How can I help you with science today?",
    "Hello! I'm an AI assistant for Integrated Science. What science topic interests you?",
    "I'm here to assist you with Integrated Science questions. What would you like to know?",
    "Hi! I'm your AI helper for Integrated Science. Feel free to ask me anything about science!",
    "I'm CeXo, an AI developed to assist you in Integrated Science. What science questions do you have?",
    "Greetings! I'm your Integrated Science AI assistant. How can I help you with science today?",
]
FOLLOW_UP_TRIGGERS = [
        "yes", "yeah", "yep", "sure", "ok", "okay", 
        "alright", "continue", "go on", "tell me more",
        "explain more", "what next", "please continue", "carry on", "more details", "further explanation", "keep going", "elaborate please",
        "i would like to know more", "can you expand on that", "please elaborate", "give me more information", "what else can you tell me", "any additional details", "more info please", "could you go deeper", "explain further", "i'm interested in more", "tell me additional information",
        "please provide more insights", "i want to learn more", "can you share more", "what other information is there", "give me further details", "i'd like to hear more", "can you elaborate on that point", "more explanation please", "what's next", "continue explaining", "go deeper into that topic",
        "please go on", "i'm curious to know more", "expand further", "tell me more about it", "what else should i know", "provide additional information", "can you tell me more about that", "i'd like more details", "give me a deeper explanation", "what more can you share", "please continue with more information",
        "elaborate on that subject", "i want further insights", "can you give me more details", "what other aspects are there", "tell me more details", "please expand on that", "i'm eager to learn more", "give me additional explanation", "what else is important to know", "continue with more info", "go further into that", "please provide further explanation",
        "tell me more information", "i'd like to understand better", "can you share additional details", "what more can you explain", "please go deeper", "i'm interested in further details", "give me more insights", "what else can you elaborate on", "continue with more details", "please tell me more", "i want to know additional information", "can you provide more explanation",
        "elaborate more on that", "i'd like to hear additional details", "give me further information", "what other details can you share", "please continue explaining", "i'm curious for more info", "expand on that topic", "tell me more insights", "what else can you provide", "please give me more details", "i want to learn additional information", "can you elaborate further",
        "more explanation on that", "i'd like further details", "give me additional insights", "what else should i understand", "please continue with more explanation", "go deeper into that topic", "tell me more about the subject", "i'm eager for more information", "can you share further details", "what other information can you provide", "please elaborate more", "i want to know further insights",
        "give me more explanation", "what else can you tell me about it", "please continue with more details", "i'm interested in additional information", "can you provide further insights", "elaborate further on that", "i'd like to understand more", "give me deeper details", "what other aspects can you explain", "please go on with more info", "tell me more about that topic", "i want to learn further details",
        "can you share more insights", "what else is there to know", "please expand further", "i'm curious for additional information", "give me more details on that", "what other information is available", "please continue with further explanation", "i'd like to hear more insights", "elaborate on that topic more", "i want additional details", "can you provide deeper explanation", "what else can you elaborate further",
        "continue with more insights", "please tell me additional information", "i'm eager to learn further details", "give me more explanation on that", "what else should i understand about it", "please go deeper into that topic", "i'd like further insights", "can you share more details on that", "what other aspects are important to know", "please continue explaining further", "tell me more about the details", 
        "i want to know deeper information", "can you elaborate on that topic more",
    ]
# follow questions from AI
FOLLOW_UP_QUESTIONS = [
        "Sure! What topic in Integrated Science would you like to explore? 😊",
        "Can you specify which area of Integrated Science you're interested in? 🤓",
        "I'd be happy to help! What specific topic in Integrated Science are you curious about? 🌟",
        "Great! Do you have a particular subject in Integrated Science you'd like to learn more about? 📚",
        "Absolutely! Which topic in Integrated Science should we dive into next? 🔬",
        "Of course! What area of Integrated Science would you like me to explain further? 🧪",
        "I'd love to assist! Could you tell me which topic in Integrated Science you're interested in? 🌍",
        "Sure thing! What specific concept in Integrated Science would you like to discuss? 💡",
        "Happy to help! Which topic in Integrated Science should we focus on? 🧬",
        "Definitely! What area of Integrated Science are you keen to explore? 🚀",
        "I'm here to help! Could you specify which topic in Integrated Science you'd like to know more about? 🔭",
        "Fantastic! What particular subject in Integrated Science are you interested in? 🌈",
        "Sure! Which topic in Integrated Science would you like me to elaborate on? 📝",
        "I'd be glad to assist! What area of Integrated Science are you curious about? 🌟",
        "Of course! What specific topic in Integrated Science would you like to learn more about? 📖",
        "Absolutely! Could you tell me which area of Integrated Science you're interested in? 🧠",
        "Great! What particular concept in Integrated Science would you like to explore? 🔍",
        "I'd love to help! Which topic in Integrated Science should we discuss next? 🌐",
        "Sure thing! What specific subject in Integrated Science are you curious about? 🧩",
        "Happy to assist! What area of Integrated Science would you like me to explain further? 🌞",
        "Definitely! Could you specify which topic in Integrated Science you'd like to know more about? 🌟",
        "I'm here to help! What particular subject in Integrated Science are you interested in? 📚",
        "Fantastic! Which topic in Integrated Science would you like me to elaborate on? 🔬",
    ]
    
CLARIFY_RESPONSES = [
    "Hmm… could you clarify your question? 🤔",
    "Sorry, what do you mean by that? 🧐",
    "I’m not sure I understand, can you rephrase?",
]

CONFIRM_PREFIXES = [
    "Yes, absolutely, ",
    "Yes, I'm sure, ",
    "Certainly, ",
    "Of course, ",
    "Definitely, ",
    "Indeed, ",
    "For sure, ",
]

FIRST_MESSAGE_TRIGGERS = ["ok", "okay", "okk", "k", "thanks", "thank you", "cool",
                            "nice", "alright", "hmm", "hmmmm", "hi", "hello"]

CLARIFICATION_QUESTIONS = [
        "What do you mean by that? 😊 Do you have a specific question in Integrated Science?",
        "I noticed your first message isn’t a question. What would you like to learn in Science?",
        "Could you explain what you meant? Any topic in Integrated Science you're curious about?",
        "Do you want to ask something related to Integrated Science? I'm ready to help!😊",
        "Could you clarify your first message for me? What topic should we explore?",
    ]
REPEAT_TOPIC_PREFIXES = [
    "Yes, as I explained earlier — ",
    "Certainly, as mentioned previously — ",
    "Indeed, like I said before — ",
    "Of course, as we discussed earlier — ",
    "Yes, earlier I noted that — ",
]

def get_random_generic_response() -> str:
    return random.choice(GENERIC_RESPONSES)

for k in SCIENCE_KNOWLEDGE.keys():
    mark_question_learned(k)
def normalize_text(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text)

# -----------------------------------------
# SAFE KNOWLEDGE RETRIEVAL (STATIC ONLY)
# -----------------------------------------

def get_all_topics() -> List[str]:
    """Return all science topics available in static KB."""
    return list(SCIENCE_KNOWLEDGE.keys())


def get_topic_facts(topic: str) -> Optional[List[str]]:
    """Return facts for a topic, if it exists in the static KB."""
    key = topic.strip().lower()
    return SCIENCE_KNOWLEDGE.get(key)


# ----------------------------------------------------
# INITIALIZATION HOOK FOR STARTUP (OPTIONAL & SAFE)
# ----------------------------------------------------
# NOTE:
#   - This function is called by FastAPI startup, NOT at import.
#   - It marks core topics as already learned in the learning_memory DB.
#   - It has NO side-effects unless explicitly invoked.


def initialize_knowledge_learning(learning_service):
    """
    During system startup, mark all static KB topics as 'learned'
    in the learning memory. Purely optional.

    Parameters
    ----------
    learning_service : module or object with method mark_question_learned(str)
    """
    for topic in SCIENCE_KNOWLEDGE.keys():
        try:
            learning_service.mark_question_learned(topic)
        except Exception:
            # Fail silently to avoid breaking startup.
            pass


# ----------------------------------------------------
# FORMATTER UTILITY
# ----------------------------------------------------

def format_answer(topic: str) -> str:
    """Return a clean, readable formatted answer from KB facts."""
    facts = get_topic_facts(topic)
    if not facts:
        return "I don't have information on that topic in my knowledge base."

    out = [f"**{topic.capitalize()}**"]
    for f in facts:
        out.append(f"- {f}")
    return "\n".join(out)
