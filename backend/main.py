from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.repository_analyzer import analyze_repository


app = FastAPI(
    title="ML Analyzer API",
    version="1.0.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Request model
# ---------------------------------------------------------

class AnalyzeRequest(BaseModel):
    repository_url: str


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "success": True,
        "message": "ML Analyzer API is running"
    }


# ---------------------------------------------------------
# Analyze repository
# ---------------------------------------------------------

@app.post("/api/analyze-project")
def analyze_project(request: AnalyzeRequest):

    try:
        result = analyze_repository(request.repository_url)

        return result

    except Exception as e:

        print("ANALYSIS ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )