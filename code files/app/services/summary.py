from app.gemini_client import generate_text

def summarize_text(text: str) -> str:
    return generate_text(f"""You are EduGenie, a study assistant. Summarize the educational passage for quick revision. Preserve important facts, definitions, relationships, and examples. Remove repetition and do not add information not contained in the passage. Use simple language and useful headings or bullets.

Educational passage:
{text}""")
