"""Minimal Postgres-backed demo for Real Estate Automation OS.

Keeps the original happy path and adds:
- persistence of agencies and audits
- stored opportunity scores
- approve modules endpoint
- simple text roadmap
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import asyncpg
import os
import uuid

app = FastAPI(title="Real Estate Automation OS", version="1.1.0")
templates = Jinja2Templates(directory="app/templates")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/realestate_os",
)

MODULES = [
    {"id": "A1", "name": "Lead Generation Engine", "domain": "Growth"},
    {"id": "A2", "name": "AI Lead Qualification", "domain": "Growth"},
    {"id": "B3", "name": "WhatsApp Communication Agent", "domain": "Sales"},
    {"id": "B5", "name": "Follow-up Automation", "domain": "Sales"},
    {"id": "C1", "name": "CRM Synchronization", "domain": "Operations"},
    {"id": "C5", "name": "Agent Productivity Assistant", "domain": "Operations"},
]


def score_module(module: dict, channels: str, pain: str) -> dict:
    base = 50
    if "whatsapp" in channels.lower() and module["id"] == "B3":
        base += 30
    if "lead" in pain.lower() and module["id"] in ("A1", "A2", "B5"):
        base += 20
    score = min(100, max(0, base + (hash(module["id"]) % 20 - 10)))
    return {
        "module_id": module["id"],
        "name": module["name"],
        "domain": module["domain"],
        "score": score,
        "priority": "immediate" if score >= 80 else "medium" if score >= 60 else "long-term",
    }


class AgencyCreate(BaseModel):
    name: str
    location: str = "Alicante, Spain"
    team_size: int = 4


class AuditCreate(BaseModel):
    agency_id: str
    channels: str = "WhatsApp, Phone"
    pain: str = "Slow response to leads"


class ApproveRequest(BaseModel):
    agency_id: str
    audit_id: str
    module_ids: List[str]


@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    async with app.state.pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS agencies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT,
                team_size INTEGER,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS audits (
                id TEXT PRIMARY KEY,
                agency_id TEXT REFERENCES agencies(id),
                channels TEXT,
                pain TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS opportunity_scores (
                id TEXT PRIMARY KEY,
                audit_id TEXT REFERENCES audits(id),
                module_id TEXT,
                name TEXT,
                domain TEXT,
                score INTEGER,
                priority TEXT
            );
            CREATE TABLE IF NOT EXISTS approved_modules (
                agency_id TEXT,
                audit_id TEXT,
                module_id TEXT,
                approved_at TIMESTAMPTZ DEFAULT NOW(),
                PRIMARY KEY (agency_id, audit_id, module_id)
            );
        """)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.post("/api/agencies")
async def create_agency(agency: AgencyCreate):
    agency_id = str(uuid.uuid4())
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO agencies (id, name, location, team_size) VALUES ($1, $2, $3, $4)",
            agency_id, agency.name, agency.location, agency.team_size,
        )
    return {"id": agency_id, "name": agency.name}


@app.post("/api/audits")
async def create_audit(audit: AuditCreate):
    audit_id = str(uuid.uuid4())
    scores = [score_module(m, audit.channels, audit.pain) for m in MODULES]
    scores.sort(key=lambda x: x["score"], reverse=True)

    async with app.state.pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO audits (id, agency_id, channels, pain) VALUES ($1, $2, $3, $4)",
            audit_id, audit.agency_id, audit.channels, audit.pain,
        )
        for s in scores:
            await conn.execute(
                """INSERT INTO opportunity_scores
                   (id, audit_id, module_id, name, domain, score, priority)
                   VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                str(uuid.uuid4()), audit_id, s["module_id"], s["name"],
                s["domain"], s["score"], s["priority"],
            )

    roadmap = build_roadmap(scores[:5])
    return {
        "audit_id": audit_id,
        "top_opportunities": scores[:5],
        "roadmap": roadmap,
    }


@app.post("/api/approve")
async def approve_modules(req: ApproveRequest):
    async with app.state.pool.acquire() as conn:
        for mid in req.module_ids:
            await conn.execute(
                """INSERT INTO approved_modules (agency_id, audit_id, module_id)
                   VALUES ($1, $2, $3) ON CONFLICT DO NOTHING""",
                req.agency_id, req.audit_id, mid,
            )
    return {"status": "approved", "modules": req.module_ids}


def build_roadmap(top: list) -> str:
    lines = ["Recommended first wave:"]
    for i, s in enumerate(top, 1):
        lines.append(f"{i}. {s['module_id']} — {s['name']} ({s['priority']}, score {s['score']})")
    lines.append("\nNext: implement the top 2–3 modules and measure response time.")
    return "\n".join(lines)


@app.get("/health")
async def health():
    return {"status": "ok", "phase": "Postgres persistence + approval"}
