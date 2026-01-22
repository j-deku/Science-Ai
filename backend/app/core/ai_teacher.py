import random

QUIZ_BANK = {
    "cell": "What is the basic unit of life?",
    "matter": "What state of matter has no fixed shape but fixed volume?"
}

def get_quiz_question():
    topic = random.choice(list(QUIZ_BANK.keys()))
    return topic, QUIZ_BANK[topic]

def validate_quiz_answer(topic: str, answer: str) -> bool:
    return topic.lower() in answer.lower()
