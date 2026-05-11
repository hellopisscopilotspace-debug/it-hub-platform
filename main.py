from fastapi import FastAPI
from pydantic import BaseModel


class IntentRequest(BaseModel):
    text: str
    language: str | None = "auto"


class IntentResponse(BaseModel):
    normalized_text: str
    detected_language: str
    notes: str


app = FastAPI(
    title="IT Hub — Public Edition",
    description="Intent-based development platform (public version)",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to IT Hub — Public Edition",
        "status": "online",
    }


@app.post("/intent", response_model=IntentResponse)
def process_intent(payload: IntentRequest):
    # Very simple placeholder logic for now
    text = payload.text.strip()

    # Fake language detection
    if any("привет" in word.lower() for word in text.split()):
        lang = "ru"
    else:
        lang = "en"

    normalized = text  # later: typo fixing, normalization, etc.

    return IntentResponse(
        normalized_text=normalized,
        detected_language=lang,
        notes="This is a placeholder Intent Engine response.",
    )
