from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from uuid import uuid4
from datetime import datetime


# ======================================
# In-memory storage (MVP version)
# ======================================

users_db = {}
projects_db = {}
ownership_db = {}


# ======================================
# Data models
# ======================================

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

    access_level: str = "basic"


class IntentRequest(BaseModel):
    user_id: str
    text: str


class ProjectResponse(BaseModel):
    project_id: str
    normalized_intent: str
    generated_code: str
    explanation: str


# ======================================
# Application
# ======================================

app = FastAPI(
    title="IT Hub Platform",
    description="Intent-based software development platform",
    version="1.0.0"
)


# ======================================
# Helper functions
# ======================================

def detect_language(text: str) -> str:
    latin_chars = "abcdefghijklmnopqrstuvwxyz"

    for char in text.lower():
        if char in latin_chars:
            return "en"

    return "unknown"


def correct_typos(text: str) -> str:

    typo_map = {
        "creat": "create",
        "bakend": "backend",
        "javscript": "javascript",
        "pyhton": "python",
        "websie": "website",
        "aplication": "application"
    }

    result = text.lower()

    for typo, correction in typo_map.items():
        result = result.replace(typo, correction)

    return result.strip()


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


def generate_explanation(style: str) -> str:

    if style == "academic":
        return (
            "The platform analyzed your request, "
            "built an execution strategy, "
            "and generated a software implementation."
        )

    if style == "philosophical":
        return (
            "Your intention was transformed into "
            "a structured digital artifact."
        )

    if style == "pragmatic":
        return (
            "You described a goal. "
            "The system generated the fastest working solution."
        )

    if style == "professional":
        return (
            "Project scaffold generated successfully."
        )

    return (
        "The system converted your idea into working code."
    )


# ======================================
# Routes
# ======================================

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
        "created_at": datetime.utcnow().isoformat(),
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


@app.post("/intent", response_model=ProjectResponse)
def process_intent(payload: IntentRequest):

    if payload.user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user_settings = users_db[payload.user_id]["settings"]

    raw_intent = payload.text.strip()

    normalized_intent = raw_intent

    if user_settings["spellcheck_enabled"]:
        normalized_intent = correct_typos(
            raw_intent
        )

    detected_language = detect_language(
        normalized_intent
    )

    generated_code = generate_code(
        normalized_intent,
        user_settings["code_language"]
    )

    explanation = generate_explanation(
        user_settings["explanation_style"]
    )

    project_id = str(uuid4())

    projects_db[project_id] = {
        "owner_id": payload.user_id,
        "intent": normalized_intent,
        "language": detected_language,
        "code": generated_code,
        "created_at": datetime.utcnow().isoformat()
    }

    ownership_db[project_id] = {
        "creator_id": payload.user_id,
        "history": [
            {
                "event": "intent_created",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "event": "code_generated",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    }

    return ProjectResponse(
        project_id=project_id,
        normalized_intent=normalized_intent,
        generated_code=generated_code,
        explanation=explanation
    )


@app.get("/projects/{user_id}")
def get_user_projects(user_id: str):

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
def get_project_ownership(project_id: str):

    if project_id not in ownership_db:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return ownership_db[project_id]
