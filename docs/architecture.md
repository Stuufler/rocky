# Architecture — From Demo MVP to Product

This document describes the intentional structure that lets the Real Estate Automation OS grow from a working demonstration into a multi-tenant product without large rewrites.

## Layers

```
┌─────────────────────────────────────────┐
│ API / UI (FastAPI routers + templates)  │
├────────────────────────────────────────┤
│ Application services (use cases)        │
├────────────────────────────────────────┤
│ Domain (models, scoring rules, modules) │
├────────────────────────────────────────┤
│ Infrastructure (DB, auth, external)     │
└────────────────────────────────────────┘
```

### 1. Domain
- Pure Python. No FastAPI, no SQLAlchemy.
- Agency, Audit, Module, OpportunityScore as Pydantic models or dataclasses.
- Scoring logic is deterministic and lives here.
- Module catalogue (the 21 modules) is a registry, not hardcoded in the API.

### 2. Application services
- Orchestrate domain objects.
- Example: `AgencyService.register()`, `AssessmentService.run_audit()`.
- Depend on repository interfaces, not concrete DB.

### 3. Infrastructure
- Concrete implementations: Postgres repositories, Supabase auth later.
- Migrations live in `migrations/`.
- For the demo: simple in-memory or single-connection Postgres. RLS policies exist in SQL but are not enforced until multi-tenancy is required.

### 4. API / UI
- Thin routers that call application services.
- Demo dashboard remains a simple Jinja page.
- Future product UI can sit on the same services.

## Transition Rules

| Stage | What is real | What is stubbed / deferred |
|-------|--------------|-----------------------------|
| Demo MVP | Registration, audit, scoring, dashboard | Multi-tenant enforcement, agents, n8n, live WhatsApp |
| Product seed | Postgres persistence, stored opportunities, approval gate | Full RLS, billing, monitoring |
| Product | Organization isolation, module marketplace, workflow factory | — |

## Module Contract

Every automation module implements:

```python
class Module(Protocol):
    id: str
    name: str
    domain: Literal["Growth", "Sales", "Operations"]

    def score(self, audit: Audit) -> OpportunityScore: ...
    def describe(self) -> str: ...
```

The registry is the single source of truth. The demo currently uses a flat list; the product will load from the same registry.

## Current Demo Path (must keep working)

1. Register agency (synthetic)
2. Capture audit
3. Score all modules
4. Show top opportunities
5. (next) Persist and allow approval

Any new code must not break this path.
