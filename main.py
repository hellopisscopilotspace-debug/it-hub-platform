from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from uuid import uuid4
from datetime import datetime


# ==========================================
# In-memory storage (MVP)
# ==========================================

users_db = {}
projects_db = {}
ownership_db = {}


# ==========================================
# Models
# ==========================================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class UserSettings(BaseModel):
    interface_language: str = "en"
    code_language: str = "python"
    explanation_language: str = "en"

    correction_mode: str = "quiet"
    explanation_style: str = "simple"

    theme: str = "dark"

    spellcheck_enabled: bool = True
    error_highlighting_enabled: bool = True

    access_level: str = "basic"


class IntentRequest(BaseModel):
    user_id: str
    text: str


class PricingResponse(BaseModel):
    access_level: str
    estimated_cost: float


class ProjectResponse(BaseModel):
    project_id: str
    normalized_intent: str
    generated_code: str
    explanation: str
    highlighted_words: list[str]
    estimated_cost: float


# ==========================================
# App
# ==========================================

app = FastAPI(
    title="IT Hub Platform",
    description="Intent-based software development platform",
    version="1.0.0"
)


# ==========================================
# Helpers
# ==========================================

def utc_now():
    return datetime.utcnow().isoformat()


def detect_language(text: str) -> str:
    latin = "abcdefghijklmnopqrstuvwxyz"

    for char in text.lower():
        if char in latin:
            return "en"

    return "unknown"


def estimate_generation_cost(access_level: str) -> float:

    pricing = {
        "basic": 0.99,
        "pro": 4.99,
        "expert": 9.99
    }

    return pricing.get(access_level, 0.99)


def correct_typos(text: str):

    typo_map = {
        "creat": "create",
        "bakend": "backend",
        "pyhton": "python",
        "javscript": "javascript",
        "websie": "website",
        "aplication": "application",
        "databse": "database"
    }

    corrected = text
    highlighted = []

    words = corrected.split()

    for i, word in enumerate(words):

        clean_word = word.lower()

        if clean_word in typo_map:

            highlighted.append(word)

            words[i] = typo_map[clean_word]

    corrected = " ".join(words)

    return corrected, highlighted


def generate_explanation(style: str) -> str:

    if style == "academic":
        return (
            "The platform analyzed the request and generated "
            "a structured implementation strategy."
        )

    if style == "philosophical":
        return (
            "Human intention was transformed into executable logic."
        )

    if style == "pragmatic":
        return (
            "The system generated the fastest working implementation."
        )

    if style == "professional":
        return (
            "Scaffold generated successfully."
        )

    return (
        "Your idea was converted into working code."
    )


def generate_code(intent: str, language: str) -> str:

    if language == "python":

        return f"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {{
        "message": "Generated from intent: {intent}"
    }}
"""

    if language == "javascript":

        return f"""
const express = require("express");

const app = express();

app.get("/", (req, res) => {{
    res.json({{
        message: "Generated from intent: {intent}"
    }});
}});
"""

    if language == "typescript":

        return f"""
import express from "express";

const app = express();

app.get("/", (req, res) => {{
    res.json({{
        message: "Generated from intent: {intent}"
    }});
}});
"""

    return f"// Generated project from intent: {intent}"


# ==========================================
# Routes
# ==========================================

@app.get("/")
def health_check():

    return {
        "platform": "IT Hub",
        "status": "online"
    }


@app.post("/register")
def register_user(payload: RegisterRequest):

    user_id = str(uuid4())

    users_db[user_id] = {
        "email": payload.email,
        "password": payload.password,
        "created_at": utc_now(),
        "settings": UserSettings().dict()
    }

    return {
        "user_id": user_id,
        "status": "registered"
    }


@app.get("/users/{user_id}")
def get_user(user_id: str):

    if user_id not in users_db:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return users_db[user_id]


@app.post("/settings/{user_id}")
def update_settings(
    user_id: str,
    settings: UserSettings
):

    if user_id not in users_db:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    users_db[user_id]["settings"] = settings.dict()

    return {
        "status": "settings_updated"
    }


@app.get("/pricing/{user_id}", response_model=PricingResponse)
def get_pricing_preview(user_id: str):

    if user_id not in users_db:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    settings = users_db[user_id]["settings"]

    access_level = settings["access_level"]

    return PricingResponse(
        access_level=access_level,
        estimated_cost=estimate_generation_cost(
            access_level
        )
    )


@app.post("/intent", response_model=ProjectResponse)
def process_intent(payload: IntentRequest):

    if payload.user_id not in users_db:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    settings = users_db[payload.user_id]["settings"]

    original_intent = payload.text.strip()

    normalized_intent = original_intent

    highlighted_words = []

    if settings["spellcheck_enabled"]:

        normalized_intent, highlighted_words = correct_typos(
            original_intent
        )

    if settings["correction_mode"] == "quiet":

        highlighted_words = []

    detected_language = detect_language(
        normalized_intent
    )

    generated_code = generate_code(
        normalized_intent,
        settings["code_language"]
    )

    explanation = generate_explanation(
        settings["explanation_style"]
    )

    estimated_cost = estimate_generation_cost(
        settings["access_level"]
    )

    project_id = str(uuid4())

    projects_db[project_id] = {
        "owner_id": payload.user_id,
        "intent": normalized_intent,
        "language": detected_language,
        "code": generated_code,
        "created_at": utc_now()
    }

    ownership_db[project_id] = {
        "creator_id": payload.user_id,
        "history": [
            {
                "event": "intent_created",
                "timestamp": utc_now()
            },
            {
                "event": "decision_completed",
                "timestamp": utc_now()
            },
            {
                "event": "code_generated",
                "timestamp": utc_now()
            }
        ]
    }

    return ProjectResponse(
        project_id=project_id,
        normalized_intent=normalized_intent,
        generated_code=generated_code,
        explanation=explanation,
        highlighted_words=highlighted_words,
        estimated_cost=estimated_cost
    )


@app.get("/projects/{user_id}")
def get_projects(user_id: str):

    results = []

    for project_id, project in projects_db.items():

        if project["owner_id"] == user_id:

            results.append({
                "project_id": project_id,
                "intent": project["intent"]
            })

    return {
        "projects": results
    }


@app.get("/ownership/{project_id}")
def get_ownership(project_id: str):

    if project_id not in ownership_db:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return ownership_db[project_id]


@app.post("/publish/github/{project_id}")
def publish_to_github(project_id: str):

    if project_id not in projects_db:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return {
        "status": "published",
        "platform": "github",
        "project_id": project_id
    }


@app.post("/publish/gitlab/{project_id}")
def publish_to_gitlab(project_id: str):

    if project_id not in projects_db:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return {
        "status": "published",
        "platform": "gitlab",
        "project_id": project_id
    }
