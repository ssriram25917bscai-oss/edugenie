from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import get_settings
from app.gemini_client import GeminiServiceError
from app.schemas import QARequest, TextRequest, TopicRequest
from app.services.explanation import explain_topic
from app.services.learning_path import get_learning_recommendations
from app.services.qna import answer_question
from app.services.quiz import generate_quiz
from app.services.summary import summarize_text

BASE_DIR=Path(__file__).resolve().parent.parent
settings=get_settings()
app=FastAPI(title=settings.app_name, description="Gemini-powered learning assistant", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR/"static")), name="static")
templates=Jinja2Templates(directory=str(BASE_DIR/"templates"))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"request":request,"app_name":settings.app_name})

@app.get("/health")
def health():
    return {"status":"ok","app":settings.app_name,"model":settings.gemini_model,"gemini_configured":bool(settings.gemini_api_key and not settings.gemini_api_key.strip().upper().startswith("YOUR_")),"demo_mode":settings.demo_mode}

def handle_ai_call(call):
    try: return call()
    except GeminiServiceError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc: raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc: raise HTTPException(status_code=500, detail=f"Unexpected server error: {exc}") from exc

@app.post("/qa")
def qa(payload: QARequest): return {"answer":handle_ai_call(lambda:answer_question(payload.question))}
@app.post("/explain")
def explain(payload: TextRequest): return {"explanation":handle_ai_call(lambda:explain_topic(payload.text))}
@app.post("/quiz")
def quiz(payload: TextRequest): return handle_ai_call(lambda:generate_quiz(payload.text)).model_dump()
@app.post("/summarize")
def summarize(payload: TextRequest): return {"summary":handle_ai_call(lambda:summarize_text(payload.text))}
@app.post("/learn/recommendations")
def recommendations(payload: TopicRequest): return handle_ai_call(lambda:get_learning_recommendations(payload.topic,payload.level)).model_dump()
