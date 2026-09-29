from app.gemini_client import generate_structured
from app.schemas import QuizResponse

def generate_quiz(passage: str) -> QuizResponse:
    result=generate_structured(f"""You are EduGenie, an educational quiz generator. Create exactly THREE multiple-choice questions from the passage. Requirements: exactly 3 questions; exactly 4 different options per question; one correct option; correct_answer exactly matches an option; include a short explanation; use only supplied passage; test understanding.

Passage:
{passage}""", QuizResponse)
    if len(result.questions)!=3: raise ValueError("Quiz generation must return exactly 3 questions.")
    for q in result.questions:
        if len(q.options)!=4 or len(set(q.options))!=4 or q.correct_answer not in q.options: raise ValueError("Quiz generation returned invalid options.")
    return result
