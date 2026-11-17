# Real Estate Automation OS
## AI-powered Operations Platform for Real Estate Agencies

**Version:** 1.0 (Foundation Phase)
**Target:** Independent agencies, boutique teams (initial: Alicante / Costa Blanca, Spain)
**Architecture:** Modular, multi-tenant, agentic, API-first

### Mission
Transform a short agency business audit into a prioritized, deployable automation architecture.
Supports full lifecycle: discovery → assessment → architecture → workflow generation → QA → deployment → monitoring.

### Tech Stack (Phase 1)
- Backend: FastAPI + Pydantic
- Database: PostgreSQL (Supabase recommended) with Row Level Security (RLS) for organization isolation
- Auth: Supabase Auth
- Agents: PydanticAI / LangGraph (later phases)
- Observability: Langfuse (later)
- Workflows: n8n integration (Phase 4)

### Project Structure
```
app/          # FastAPI application
models/       # SQLAlchemy / DB models
schemas/      # Pydantic schemas
agents/       # Discovery, Assessment, Architect agents
registry/     # Technology Capability Registry
migrations/   # Alembic or SQL migrations
tests/
docs/
```

### Getting Started
1. Copy `.env.example` to `.env` and fill credentials
2. `docker-compose up -d` (for local Postgres) or connect to Supabase
3. `pip install -r requirements.txt`
4. `uvicorn app.main:app --reload`

### Demo UI (Level 1)
```bash
cd real-estate-automation-os
pip install -r requirements.txt
uvicorn app.main:app --reload
# Open http://localhost:8000
```

Features in demo:
- Register synthetic agency
- Run operational audit
- Score all 21 modules and show top opportunities

In-memory store for now (Postgres + RLS next).

### High-value infrastructure selected
See `docs/tech-registry-analysis.md` (from Awesome Agent Infrastructure).
Key: mem0, Langfuse, n8n-mcp, deepeval, ragas, Playwright.
