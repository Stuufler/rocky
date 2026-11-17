"""Domain models for Real Estate Automation OS.

Pure data structures. No I/O, no framework dependencies.
"""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Agency(BaseModel):
    id: Optional[str] = None
    name: str
    location: str = "Alicante, Spain"
    team_size: int = 3
    specialization: Optional[str] = None
    website: Optional[str] = None
    created_at: Optional[datetime] = None


class Audit(BaseModel):
    id: Optional[str] = None
    agency_id: str
    channels: str = "WhatsApp, Phone"
    pain: str = ""
    existing_crm: Optional[str] = None
    objectives: Optional[str] = None
    created_at: Optional[datetime] = None


class OpportunityScore(BaseModel):
    module_id: str
    name: str
    domain: Literal["Growth", "Sales", "Operations"]
    score: int = Field(ge=0, le=100)
    revenue_impact: Literal["low", "medium", "high"]
    priority: Literal["immediate", "medium", "long-term"]
    time_savings_hours: float = 0.0
    reason: str = ""
