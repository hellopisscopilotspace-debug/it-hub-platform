from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from uuid import uuid4
from datetime import datetime


# ==================================================
# In-memory storage
# ==================================================

users_db = {}
projects_db = {}
ownership_db = {}
marketplace_db = {}


# ==================================================
# Models
# ==================================================

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
    output_type: str


class PricingResponse(BaseModel):
    access_level: str
    estimated_cost: float


class MarketplaceRequest(BaseModel):
    user_id: str
    project_id: str
    asset_name: str
    asset_type: str
    is_private: bool = False


class ProjectResponse(BaseModel):
    project_id: str
    normalized_intent: str
    output_type: str
    decision_plan: list[str]
    generated_code: str
    explanation: str
    highlighted_words: list[str]
    estimated_cost: float


# ==================================================
# App
# ==================================================

app = FastAPI(
    title="IT Hub Platform",
    description="Intent-based software development platform",
    version="1.0.0"
)


# ==================================================
# Helpers
# ==================================================

def now():
    return datetime.utcnow().isoformat()


def detect_language(text: str):

    latin = "abcdefghijklmnopqrstuvwxyz"

    for char in text.lower():
        if char in latin:
            return "en"

    return "unknown"


def estimate_price(level: str):

    price_map = {
        "basic": 0.99,
        "pro": 4.99,
        "expert": 9.99
    }

    return price_map.get(level, 0.99)


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

    words = text.split()

    highlighted = []

    for i, word in enumerate(words):

        normalized = word.lower()

        if normalized in typo_map:

            highlighted.append(word)

            words[i] = typo_map[normalized]

    corrected = " ".join(words)

    return corrected, highlighted


def build_decision_plan(output_type: str):

    plans = {
        "web_app": [
            "create_routes",
            "create_ui_structure",
            "connect_database",
            "prepare_deployment"
        ],

        "mobile_app": [
            "create_mobile_structure",
            "create_screens",
            "connect_api",
            "prepare_build"
        ],

        "api_service": [
            "create_endpoints",
            "add_validation",
            "connect_database",
            "prepare_documentation"
        ],

        "game_prototype": [
            "create_game_loop",
            "create_scene_structure",
            "create_input_system"
        ],

        "saas_platform": [
            "create_authentication",
            "create_subscription_logic",
            "create_dashboard"
        ]
    }

    return plans.get(
        output_type,
        [
            "analyze_request",
            "generate_architecture",
            "generate_output"
        ]
    )


def generate_code(
    intent: str,
    language: str,
    output_type: str
):

    if language == "python":

        return f"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {{
        "output_type": "{output_type}",
        "intent": "{intent}"
    }}
"""

    if language == "javascript":

        return f"""
const express = require("express");

const app = express();

app.get("/", (req, res) => {{
    res.json({{
        output_type: "{output_type}",
        intent: "{intent}"
    }});
}});
"""

    if language == "typescript":

        return f"""
import express from "express";

const app = express();

app.get("/", (req, res) => {{
    res.json({{
        output_type: "{output_type}",
        intent: "{intent}"
    }});
}});
"""

    return f"// Generated from: {intent}"


def generate_explanation(
    style: str,
    output_type: str
):

    if style == "academic":

        return (
            f"The system analyzed your request and "
            f"generated a structured {output_type} implementation."
        )

    if style == "philosophical":

        return (
            f"Your intention became an executable "
            f"{output_type} architecture."
        )

    if style == "pragmatic":

        return (
            f"The system generated the fastest "
            f"working {output_type} solution."
        )

    if style == "professional":

        return (
            f"{output_type} scaffold generated successfully."
        )

    return (
        f"Your idea was converted into a "
        f"{output_type} implementation."
    )


# ==================================================
# Routes
# ==================================================

@app.get("/")
def root():

    return {
        "platform": "IT Hub",
        "status": "online"
    }


@app.post("/register")
def register(payload: RegisterRequest):

    user_id = str(uuid4())

    users_db[user_id] = {
        "email": payload.email,
        "password": payload.password,
        "created_at": now(),
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
        "status": "updated"
    }


@app.get("/pricing/{user_id}")
def pricing(user_id: str):

    if user_id not in users_db:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    settings = users_db[user_id]["settings"]

    return PricingResponse(
        access_level=settings["access_level"],
        estimated_cost=estimate_price(
            settings["access_level"]
        )
    )


@app.post("/intent")
def process_intent(
    payload: IntentRequest
):

    if payload.user_id not in users_db:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    settings = users_db[payload.user_id]["settings"]

    corrected_text, highlighted = correct_typos(
        payload.text
    )

    if settings["correction_mode"] == "quiet":

        highlighted = []

    detected_language = detect_language(
        corrected_text
    )

    decision_plan = build_decision_plan(
        payload.output_type
    )

    generated_code = generate_code(
        corrected_text,
        settings["code_language"],
        payload.output_type
    )

    explanation = generate_explanation(
        settings["explanation_style"],
        payload.output_type
    )

    estimated_cost = estimate_price(
        settings["access_level"]
    )

    project_id = str(uuid4())

    projects_db[project_id] = {
        "owner_id": payload.user_id,
        "intent": corrected_text,
        "output_type": payload.output_type,
        "language": detected_language,
        "decision_plan": decision_plan,
        "code": generated_code,
        "created_at": now()
    }

    ownership_db[project_id] = {
        "creator_id": payload.user_id,
        "history": [
            {
                "event": "intent_created",
                "timestamp": now()
            },
            {
                "event": "decision_completed",
                "timestamp": now()
            },
            {
                "event": "code_generated",
                "timestamp": now()
            },
            {
                "event": "validation_completed",
                "timestamp": now()
            }
        ]
    }

    return ProjectResponse(
        project_id=project_id,
        normalized_intent=corrected_text,
        output_type=payload.output_type,
        decision_plan=decision_plan,
        generated_code=generated_code,
        explanation=explanation,
        highlighted_words=highlighted,
        estimated_cost=estimated_cost
    )


@app.get("/projects/{user_id}")
def get_projects(user_id: str):

    results = []

    for project_id, project in projects_db.items():

        if project["owner_id"] == user_id:

            results.append({
                "project_id": project_id,
                "intent": project["intent"],
                "output_type": project["output_type"]
            })

    return {
        "projects": results
    }


@app.get("/ownership/{project_id}")
def ownership(project_id: str):

    if project_id not in ownership_db:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return ownership_db[project_id]


@app.post("/publish/github/{project_id}")
def publish_github(project_id: str):

    if project_id not in projects_db:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return {
        "status": "published",
        "platform": "github"
    }


@app.post("/publish/gitlab/{project_id}")
def publish_gitlab(project_id: str):

    if project_id not in projects_db:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return {
        "status": "published",
        "platform": "gitlab"
    }


@app.post("/marketplace/publish")
def publish_marketplace(
    payload: MarketplaceRequest
):

    if payload.project_id not in projects_db:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    asset_id = str(uuid4())

    marketplace_db[asset_id] = {
        "creator_id": payload.user_id,
        "project_id": payload.project_id,
        "asset_name": payload.asset_name,
        "asset_type": payload.asset_type,
        "is_private": payload.is_private,
        "commission_enabled": not payload.is_private,
        "created_at": now()
    }

    return {
        "asset_id": asset_id,
        "published": True,
        "commission_enabled": (
            not payload.is_private
        )
    }


@app.get("/marketplace")
def marketplace():

    assets = []

    for asset_id, asset in marketplace_db.items():

        if not asset["is_private"]:

            assets.append({
                "asset_id": asset_id,
                "asset_name": asset["asset_name"],
                "asset_type": asset["asset_type"]
            })

    return {
        "assets": assets
    }
