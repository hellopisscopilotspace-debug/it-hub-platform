from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime


ownership_store = {}


class IntentRequest(BaseModel):
    user_id: str
    text: str
    language: str | None = "auto"


class IntentResponse(BaseModel):
    project_id: str
    normalized_text: str
    detected_language: str
    notes: str


app = FastAPI(
    title="IT Hub — Public Edition",
    version="0.2.0",
)


@app.get("/")
def root():
    return {
        "status": "online"
    }


@app.post("/intent", response_model=IntentResponse)
def process_intent(payload: IntentRequest):

    text = payload.text.strip()

    if any("привет" in word.lower() for word in text.split()):
        lang = "ru"
    else:
        lang = "en"

    project_id = str(uuid4())

    ownership_store[project_id] = {
        "creator": payload.user_id,
        "created_at": datetime.utcnow().isoformat(),
        "history": [
            {
                "event": "intent_created",
                "text": text,
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    }

    return IntentResponse(
        project_id=project_id,
        normalized_text=text,
        detected_language=lang,
        notes="Intent captured and ownership chain created."
    )


@app.get("/ownership/{project_id}")
def get_ownership(project_id: str):

    return ownership_store.get(
        project_id,
        {
            "error": "Project not found"
        }
    )
