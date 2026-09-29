# EduGenie — Fixed MVP

FastAPI + Google Gemini learning assistant with Q&A, explanations, quizzes, summaries, and learning recommendations.

## What was fixed

- Fixed FastAPI/Starlette `TemplateResponse` usage.
- Fixed static file paths.
- Updated `google-genai` dependency to the current 2.x API used by this project.
- Added safe Demo Mode so the complete UI and endpoints can be tested without Gemini credentials.
- Added clearer Gemini 401/403/429 error messages.
- Prevented placeholder API keys from being treated as real credentials.
- Kept quiz and learning-path output validation with Pydantic.
- `/health` reports Gemini configuration and Demo Mode status.

## Windows setup

```powershell
cd C:\Users\SDCLAB2\Downloads\edugenie
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create `.env` from `.env.example`.

### Test the application immediately (no API key)

Keep:

```env
DEMO_MODE=true
GEMINI_API_KEY=
```

Then:

```powershell
python -m uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

### Use live Gemini

After obtaining a valid Gemini API key, set:

```env
GEMINI_API_KEY=YOUR_REAL_KEY
GEMINI_MODEL=gemini-3.8-flash
DEMO_MODE=false
```

Restart Uvicorn after changing `.env`.

If live Gemini returns `401 ACCESS_TOKEN_TYPE_UNSUPPORTED`, the request is reaching Google but the credential is being rejected. Replace the key with a valid Gemini API key; do not put an OAuth bearer token in `GEMINI_API_KEY`.

## Test

```powershell
python -m pytest -q
```

## Endpoints

- `GET /`
- `GET /health`
- `POST /qa`
- `POST /explain`
- `POST /quiz`
- `POST /summarize`
- `POST /learn/recommendations`
