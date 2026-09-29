from functools import lru_cache

from google import genai
from google.genai import types

from app.config import get_settings


class GeminiServiceError(RuntimeError):
    """Raised when Gemini cannot complete a request."""


def _clean_key(value: str) -> str:
    """Remove accidental surrounding whitespace/quotes from an env value."""
    value = (value or "").strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1].strip()
    return value


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    settings = get_settings()
    key = _clean_key(settings.gemini_api_key)

    if not key or key.upper().startswith("YOUR_"):
        raise GeminiServiceError(
            "GEMINI_API_KEY is not configured. Add a real Gemini API key to .env."
        )

    try:
        return genai.Client(api_key=key)
    except Exception as exc:
        raise GeminiServiceError(f"Could not initialize Gemini client: {exc}") from exc


def _is_configured() -> bool:
    key = _clean_key(get_settings().gemini_api_key)
    return bool(key) and not key.upper().startswith("YOUR_")


def _friendly_gemini_error(exc: Exception) -> str:
    message = str(exc)
    if "401" in message or "UNAUTHENTICATED" in message or "ACCESS_TOKEN_TYPE_UNSUPPORTED" in message:
        return (
            "Gemini authentication failed (401). Your EduGenie code is reaching Google, "
            "but the API key is not accepted. Create/copy a valid Gemini API key in "
            "Google AI Studio, put it in .env as GEMINI_API_KEY=..., then restart Uvicorn. "
            "Do not use an OAuth access token as GEMINI_API_KEY."
        )
    if "403" in message or "PERMISSION_DENIED" in message:
        return (
            "Gemini permission was denied (403). Check that the API key/project is "
            "allowed to use the Gemini API and that the selected model is available."
        )
    if "429" in message or "RESOURCE_EXHAUSTED" in message:
        return "Gemini rate/quota limit reached (429). Wait and try again or check your quota."
    return f"Gemini request failed: {message}"


def generate_text(prompt: str) -> str:
    settings = get_settings()

    if settings.demo_mode:
        return demo_text(prompt)

    if not _is_configured():
        raise GeminiServiceError(
            "GEMINI_API_KEY is not configured. Set GEMINI_API_KEY in .env or enable DEMO_MODE=true."
        )

    try:
        response = get_client().models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=2048,
            ),
        )
        text = (response.text or "").strip()
        if not text:
            raise GeminiServiceError("Gemini returned an empty response.")
        return text
    except GeminiServiceError:
        raise
    except Exception as exc:
        raise GeminiServiceError(_friendly_gemini_error(exc)) from exc


def generate_structured(prompt: str, response_model):
    settings = get_settings()

    if settings.demo_mode:
        return demo_structured(response_model, prompt)

    if not _is_configured():
        raise GeminiServiceError(
            "GEMINI_API_KEY is not configured. Set GEMINI_API_KEY in .env or enable DEMO_MODE=true."
        )

    try:
        response = get_client().models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=4096,
                response_mime_type="application/json",
                response_schema=response_model,
            ),
        )

        parsed = getattr(response, "parsed", None)
        if parsed is not None:
            if isinstance(parsed, response_model):
                return parsed
            return response_model.model_validate(parsed)

        text = (response.text or "").strip()
        if not text:
            raise GeminiServiceError("Gemini returned an empty structured response.")
        return response_model.model_validate_json(text)
    except GeminiServiceError:
        raise
    except Exception as exc:
        raise GeminiServiceError(_friendly_gemini_error(exc)) from exc


def _extract_prompt_value(prompt: str, label: str, default: str = "") -> str:
    marker = f"{label}:"
    if marker not in prompt:
        return default
    value = prompt.split(marker, 1)[1].strip()
    return value.split("\n", 1)[0].strip() or default


def demo_text(prompt: str) -> str:
    lower = prompt.lower()
    if "student question" in lower:
        question = _extract_prompt_value(prompt, "Student question", "your question")
        return (
            f"Demo answer for: {question}\n\n"
            "EduGenie is running in Demo Mode, so this response is generated locally. "
            "Set DEMO_MODE=false and add a valid GEMINI_API_KEY in .env to use live Gemini."
        )

    if "educational passage" in lower:
        passage = _extract_prompt_value(prompt, "Educational passage", "the supplied text")
        return (
            "Demo summary\n\n"
            f"The supplied study text begins with: {passage[:500]}\n\n"
            "Set DEMO_MODE=false and configure a valid Gemini API key for live summarization."
        )

    topic = _extract_prompt_value(prompt, "Topic", "the requested topic")
    return (
        f"Demo explanation of {topic}\n\n"
        "1. Simple definition: This is a demonstration response.\n"
        "2. Main idea: EduGenie would explain the concept step by step.\n"
        "3. Example: Configure Gemini for a topic-specific example.\n"
        "4. Remember: Set DEMO_MODE=false to use live Gemini."
    )


def demo_structured(response_model, prompt: str):
    from app.schemas import LearningPathResponse, LearningStep, QuizQuestion, QuizResponse

    if response_model is QuizResponse:
        return QuizResponse(
            questions=[
                QuizQuestion(
                    question="What is the main purpose of EduGenie?",
                    options=["Educational assistance", "Video editing", "Image compression", "File backup"],
                    correct_answer="Educational assistance",
                    explanation="EduGenie is an educational learning assistant.",
                ),
                QuizQuestion(
                    question="How many questions does the quiz endpoint return?",
                    options=["1", "2", "3", "5"],
                    correct_answer="3",
                    explanation="The quiz contract requires exactly three questions.",
                ),
                QuizQuestion(
                    question="Which backend framework does EduGenie use?",
                    options=["FastAPI", "Flask", "Django", "Express"],
                    correct_answer="FastAPI",
                    explanation="The backend is implemented with FastAPI.",
                ),
            ]
        )

    if response_model is LearningPathResponse:
        topic = _extract_prompt_value(prompt, "Topic", "the selected topic")
        level = _extract_prompt_value(prompt, "Current learner level", "beginner")
        return LearningPathResponse(
            topic=topic,
            level=level,
            overview="Demo learning path. Configure Gemini for a personalized plan.",
            steps=[
                LearningStep(stage="Beginner", topics=[f"{topic} basics", "Core vocabulary"], estimated_time="2–3 hours", resources=["Beginner textbook or tutorial"]),
                LearningStep(stage="Intermediate", topics=[f"{topic} applications", "Practice problems"], estimated_time="4–6 hours", resources=["Practice exercises", "Intermediate tutorial"]),
                LearningStep(stage="Advanced", topics=[f"Advanced {topic}", "Mini project"], estimated_time="6–10 hours", resources=["Advanced documentation", "Project-based practice"]),
            ],
        )

    raise GeminiServiceError(f"Demo structured output is not implemented for {response_model.__name__}.")
