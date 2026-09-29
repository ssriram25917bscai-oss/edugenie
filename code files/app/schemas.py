from typing import Literal
from pydantic import BaseModel, Field, field_validator

class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=30000)
    @field_validator("text")
    @classmethod
    def clean_text(cls, value: str) -> str:
        value=value.strip()
        if not value: raise ValueError("Input cannot be empty.")
        return value

class QARequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    @field_validator("question")
    @classmethod
    def clean_question(cls, value: str) -> str:
        value=value.strip()
        if not value: raise ValueError("Question cannot be empty.")
        return value

class TopicRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)
    level: Literal["beginner","intermediate","advanced"] = "beginner"
    @field_validator("topic")
    @classmethod
    def clean_topic(cls, value: str) -> str:
        value=value.strip()
        if not value: raise ValueError("Topic cannot be empty.")
        return value

class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    correct_answer: str
    explanation: str

class QuizResponse(BaseModel):
    questions: list[QuizQuestion] = Field(min_length=3, max_length=3)

class LearningStep(BaseModel):
    stage: Literal["Beginner","Intermediate","Advanced"]
    topics: list[str]
    estimated_time: str
    resources: list[str]

class LearningPathResponse(BaseModel):
    topic: str
    level: str
    overview: str
    steps: list[LearningStep]
