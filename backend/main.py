from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.repository_analyzer import analyze_repository

app = FastAPI(
    title="ML Analyzer API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    repository_url: str


@app.get("/health")
def health():
    return {
        "success": True,
        "message": "ML Analyzer API is running"
    }


@app.post("/api/analyze-project")
def analyze_project(request: AnalyzeRequest):
    try:
        return analyze_repository(request.repository_url)
    except Exception as e:
        print("ANALYSIS ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


FRONTEND_DIST = (
    Path(__file__).resolve().parent.parent
    / "frontend"
    / "dist"
)

app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIST), html=True),
    name="frontend"
)
