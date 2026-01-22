import re

def hallucination_blocker(question: str, answer: str) -> str | None:
    if len(answer.split()) < 3:
        return "❗ I don’t want to guess — can you clarify your question?"

    if re.search(r"(i think|maybe|possibly)", answer.lower()):
        return "⚠ I’m not fully confident about that. Can you be more specific?"

    if "?" in answer:
        return "Hmm, I’m unsure. Could you rephrase?"

    return None
import re

def hallucination_blocker(question: str, answer: str) -> str | None:
    if len(answer.split()) < 3:
        return "❗ I don’t want to guess — can you clarify your question?"

    if re.search(r"(i think|maybe|possibly)", answer.lower()):
        return "⚠ I’m not fully confident about that. Can you be more specific?"

    if "?" in answer:
        return "Hmm, I’m unsure. Could you rephrase?"

    return None
