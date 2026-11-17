from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
from datetime import datetime

app = FastAPI(title="Real Estate Automation OS", version="1.0.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# In-memory store for demo (replace with Postgres later)
agencies_db: Dict[str, dict] = {}
audits_db: Dict[str, dict] = {}

MODULES = [
    {"id": "A1", "name": "Lead Generation Engine", "domain": "Growth"},
    {"id": "A2", "name": "AI Lead Qualification", "domain": "Growth"},
    {"id": "A3", "name": "Property Acquisition Agent", "domain": "Growth"},
    {"id": "A4", "name": "Marketing Content Engine", "domain": "Growth"},
    {"id": "A5", "name": "Property Listing Intelligence", "domain": "Growth"},
    {"id": "A6", "name": "Market & Competitor Intelligence", "domain": "Growth"},
    {"id": "A7", "name": "Lead Reactivation Engine", "domain": "Growth"},
    {"id": "B1", "name": "Buyer Matching Engine", "domain": "Sales"},
    {"id": "B2", "name": "AI Sales Assistant", "domain": "Sales"},
    {"id": "B3", "name": "WhatsApp Communication Agent", "domain": "Sales"},
    {"id": "B4", "name": "Viewing Scheduler", "domain": "Sales"},
    {"id": "B5", "name": "Follow-up Automation", "domain": "Sales"},
    {"id": "B6", "name": "Offer & Negotiation Assistant", "domain": "Sales"},
    {"id": "B7", "name": "Transaction Coordination", "domain": "Sales"},
    {"id": "C1", "name": "CRM Synchronization", "domain": "Operations"},
    {"id": "C2", "name": "Document Intelligence", "domain": "Operations"},
    {"id": "C3", "name": "Agency Knowledge Assistant", "domain": "Operations"},
    {"id": "C4", "name": "Performance & Revenue Analytics", "domain": "Operations"},
    {"id": "C5", "name": "Agent Productivity Assistant", "domain": "Operations"},
    {"id": "C6", "name": "Automation Monitoring", "domain": "Operations"},
    {"id": "C7", "name": "Commission Management", "domain": "Operations"},
]

def score_module(module: dict, audit: dict) -> dict:
    """Deterministic scoring based on audit (synthetic for demo)."""
    base = 50
    if "whatsapp" in str(audit.get("channels", "")).lower() and module["id"] == "B3":
        base += 30
    if audit.get("team_size", 0) > 5 and module["id"] in ["C5", "B5"]:
        base += 15
    if "lead" in str(audit.get("pain", "")).lower() and module["id"] in ["A1", "A2", "B5"]:
        base += 20
    score = min(100, max(0, base + (hash(module["id"]) % 20 - 10)))
    return {
        "module_id": module["id"],
        "name": module["name"],
        "domain": module["domain"],
        "score": score,
        "revenue_impact": "high" if score > 75 else "medium" if score > 50 else "low",
        "time_savings_hours": round(score / 10, 1),
        "priority": "immediate" if score >= 80 else "medium" if score >= 60 else "long-term"
    }

class AgencyCreate(BaseModel):
    name: str
    website: Optional[str] = None
    location: str = "Alicante, Spain"
    team_size: Optional[int] = 3
    specialization: Optional[str] = "Residential"

class AuditCreate(BaseModel):
    agency_id: str
    lead_sources: Optional[str] = "Website, WhatsApp, Idealista"
    channels: Optional[str] = "WhatsApp, Phone, Email"
    pain: Optional[str] = "Slow lead response, manual follow-up"
    existing_crm: Optional[str] = "None / Spreadsheets"
    objectives: Optional[str] = "More qualified leads and faster viewings"

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "agencies": list(agencies_db.values()),
        "module_count": len(MODULES)
    })

@app.post("/api/agencies")
async def create_agency(agency: AgencyCreate):
    agency_id = str(uuid.uuid4())
    record = {
        "id": agency_id,
        "name": agency.name,
        "website": agency.website,
        "location": agency.location,
        "team_size": agency.team_size,
        "specialization": agency.specialization,
        "created_at": datetime.utcnow().isoformat()
    }
    agencies_db[agency_id] = record
    return record

@app.post("/api/audits")
async def create_audit(audit: AuditCreate):
    if audit.agency_id not in agencies_db:
        return {"error": "Agency not found"}
    audit_id = str(uuid.uuid4())
    record = audit.model_dump()
    record["id"] = audit_id
    record["created_at"] = datetime.utcnow().isoformat()
    audits_db[audit_id] = record
    # Score all modules
    scores = [score_module(m, record) for m in MODULES]
    scores.sort(key=lambda x: x["score"], reverse=True)
    return {
        "audit_id": audit_id,
        "agency_id": audit.agency_id,
        "top_opportunities": scores[:5],
        "all_scores": scores,
        "recommendation": "Focus on top 3-5 modules for first implementation wave."
    }

@app.get("/api/modules")
async def list_modules():
    return MODULES

@app.get("/health")
async def health():
    return {"status": "healthy", "phase": "Level 1 Demo"}
