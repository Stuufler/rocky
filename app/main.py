"""Minimal demo with optional n8n webhook after module approval."""

import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import asyncpg
import uuid

app = FastAPI(title="Real Estate Automation OS", version="1.2.0")
templates = Jinja2Templates(directory="app/templates")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/realestate_os")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")

MODULES = [
    {"id": "A1", "name": "Lead Generation Engine", "domain": "Growth"},
    {"id": "B3", "name": "WhatsApp Communication Agent", "domain": "Sales"},
    {"id": "B5", "name": "Follow-up Automation", "domain": "Sales"},
    {"id": "C1", "name": "CRM Synchronization", "domain": "Operations"},
]

def score_module(module: dict, channels: str, pain: str) -> dict:
    base = 50
    if "whatsapp" in channels.lower() and module["id"] == "B3":
        base += 30
    if "lead" in pain.lower() and module["id"] in ("A1", "B5"):
        base += 20
    score = min(100, max(0, base + (hash(module["id"]) % 20 - 10)))
    return {
        "module_id": module["id"],
        "name": module["name"],
        "score": score,
        "priority": "immediate" if score >= 80 else "medium" if score >= 60 else "long-term",
    }

class AgencyCreate(BaseModel):
    name: str

class AuditCreate(BaseModel):
    agency_id: str
    channels: str = "WhatsApp"
    pain: str = "Slow leads"

class ApproveRequest(BaseModel):
    agency_id: str
    audit_id: str
    module_ids: List[str]

@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=3)
    async with app.state.pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS agencies (id TEXT PRIMARY KEY, name TEXT, created_at TIMESTAMPTZ DEFAULT NOW());
            CREATE TABLE IF NOT EXISTS audits (id TEXT PRIMARY KEY, agency_id TEXT, channels TEXT, pain TEXT);
            CREATE TABLE IF NOT EXISTS approved_modules (agency_id TEXT, audit_id TEXT, module_id TEXT, PRIMARY KEY (agency_id, audit_id, module_id));
        """)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "n8n_configured": bool(N8N_WEBHOOK_URL)})

@app.post("/api/agencies")
async def create_agency(agency: AgencyCreate):
    agency_id = str(uuid.uuid4())
    async with app.state.pool.acquire() as conn:
        await conn.execute("INSERT INTO agencies (id, name) VALUES ($1, $2)", agency_id, agency.name)
    return {"id": agency_id, "name": agency.name}

@app.post("/api/audits")
async def create_audit(audit: AuditCreate):
    audit_id = str(uuid.uuid4())
    scores = sorted([score_module(m, audit.channels, audit.pain) for m in MODULES], key=lambda x: x["score"], reverse=True)
    async with app.state.pool.acquire() as conn:
        await conn.execute("INSERT INTO audits (id, agency_id, channels, pain) VALUES ($1, $2, $3, $4)",
                           audit_id, audit.agency_id, audit.channels, audit.pain)
    roadmap = "\n".join([f"{i}. {s['module_id']} — {s['name']} ({s['score']})" for i, s in enumerate(scores[:3], 1)])
    return {"audit_id": audit_id, "top_opportunities": scores[:3], "roadmap": roadmap}

@app.post("/api/approve")
async def approve_modules(req: ApproveRequest):
    async with app.state.pool.acquire() as conn:
        for mid in req.module_ids:
            await conn.execute(
                "INSERT INTO approved_modules (agency_id, audit_id, module_id) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
                req.agency_id, req.audit_id, mid,
            )

    payload = {
        "agency_id": req.agency_id,
        "audit_id": req.audit_id,
        "modules": req.module_ids,
        "source": "reaos-demo",
    }

    n8n_result = None
    if N8N_WEBHOOK_URL:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.post(N8N_WEBHOOK_URL, json=payload)
                n8n_result = {"status_code": r.status_code, "ok": r.is_success}
        except Exception as e:
            n8n_result = {"error": str(e)}

    return {"status": "approved", "modules": req.module_ids, "n8n": n8n_result}

@app.get("/api/n8n/export")
async def export_for_n8n(agency_id: str, audit_id: str):
    return {
        "webhook_payload": {
            "agency_id": agency_id,
            "audit_id": audit_id,
            "modules": [],
            "note": "Fill modules and POST to your n8n webhook",
        },
        "workflow_file": "workflows/reaos-approved-modules.json",
    }

@app.get("/health")
async def health():
    return {"status": "ok", "n8n_webhook_configured": bool(N8N_WEBHOOK_URL)}
