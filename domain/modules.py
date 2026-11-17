"""Module registry — single source of truth for the 21 modules.

Scoring stays deterministic. Each module can later grow its own strategy
without changing the API or UI.
"""

from typing import Protocol
from domain.models import Audit, OpportunityScore


class Module(Protocol):
    id: str
    name: str
    domain: str

    def score(self, audit: Audit) -> OpportunityScore: ...


# Flat list used by the current demo. Will become a proper registry.
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


def score_module(module: dict, audit: Audit) -> OpportunityScore:
    """Deterministic scoring used by the demo. Extracted so it can be replaced later."""
    base = 50
    if "whatsapp" in audit.channels.lower() and module["id"] == "B3":
        base += 30
    if audit.pain and "lead" in audit.pain.lower() and module["id"] in ("A1", "A2", "B5"):
        base += 20
    score = min(100, max(0, base + (hash(module["id"]) % 20 - 10)))
    return OpportunityScore(
        module_id=module["id"],
        name=module["name"],
        domain=module["domain"],
        score=score,
        revenue_impact="high" if score > 75 else "medium" if score > 50 else "low",
        priority="immediate" if score >= 80 else "medium" if score >= 60 else "long-term",
        time_savings_hours=round(score / 10, 1),
        reason="Rule-based score for demo",
    )
