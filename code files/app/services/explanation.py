from app.config import get_settings
from app.gemini_client import generate_text
_local_pipeline=None

def _local_explanation(topic: str) -> str:
    global _local_pipeline
    from transformers import pipeline
    if _local_pipeline is None:
        settings=get_settings(); _local_pipeline=pipeline("text2text-generation", model=settings.local_explanation_model, tokenizer=settings.local_explanation_model)
    result=_local_pipeline(f"Explain this to a beginner with a simple example: {topic}", max_new_tokens=180, do_sample=False)
    return result[0]["generated_text"].strip()

def explain_topic(topic: str) -> str:
    settings=get_settings()
    if settings.local_explanation_enabled:
        try: return _local_explanation(topic)
        except Exception: pass
    return generate_text(f"""You are EduGenie, a patient teacher. Explain the concept below to a student with little previous knowledge. Use: 1. Simple definition 2. Main idea 3. Easy example or analogy 4. Important points to remember. Use clear concise language.

Topic:
{topic}""")
