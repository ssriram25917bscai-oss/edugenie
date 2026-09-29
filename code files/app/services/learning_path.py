from app.gemini_client import generate_structured
from app.schemas import LearningPathResponse


def get_learning_recommendations(topic: str, level: str) -> LearningPathResponse:
    prompt = f"""You are EduGenie, a personalized educational planning assistant.

Create a practical self-learning path for the following learner.

Topic:
{topic}

Current learner level:
{level}

Create exactly three stages: Beginner, Intermediate, Advanced.
For every stage provide topics, estimated learning time, and useful resource names/types.
Progress logically. Do not fabricate URLs.
"""
    return generate_structured(prompt, LearningPathResponse)
