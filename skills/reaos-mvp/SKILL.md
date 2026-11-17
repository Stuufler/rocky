---
name: reaos-mvp
description: "Guide progressive, minimal implementation of Real Estate Automation OS as a working demo MVP. Use when continuing development of the agency automation platform, adding features, refining architecture, or planning next steps while avoiding anti-patterns, over-engineering, and unnecessary complexity."
type: workflow
lifecycle: active
---

# REAOS MVP — Minimal Working Demo Architecture

Build and deepen the Real Estate Automation OS as a **working demonstration product**. Prioritize clarity, correctness, and the smallest possible surface that shows value. Avoid premature multi-tenancy complexity, full agent orchestration, and production hardening until the demo path is solid.

## Core Principles (always apply)

1. **Minimal viable** — implement only what is required for the current demo scenario. No speculative features.
2. **Deterministic first** — prefer typed Python and explicit logic over LLM calls for scoring, routing, and state transitions.
3. **Single tenant for demo** — multi-tenant isolation (RLS) is designed but not enforced until two agencies must coexist.
4. **One vertical path** — the Alicante boutique agency WhatsApp → qualification → matching → follow-up flow must work end-to-end before adding breadth.
5. **Explicit contracts** — every module has clear input/output schemas. No hidden side effects.
6. **Human approval gates** — any action that could send a message or change a deal requires an explicit approval step in the demo.

## Current Demo Scope (Level 1)

- Agency registration (synthetic data)
- Operational audit capture
- Scoring of the 21 modules with explainable reasons
- Top-5 opportunity report
- Simple web dashboard to walk through the flow

## Workflow

1. Confirm the request stays inside the current demo boundary. If it expands scope, propose a smaller alternative first.
2. Check existing code in the repository (FastAPI app, schema, dashboard).
3. Implement the smallest change that advances the demo path.
4. Keep data in-memory or a single Postgres table until persistence is required for the demo.
5. Add a short note in CHANGELOG of the skill or a project note when a design decision is made.
6. Verify the happy path still works after the change.

## Architecture Guardrails

| Area | Do | Avoid |
|------|----|-------|
| Data | Single `organizations` / `agencies` tables, synthetic seed | Full RLS policies, separate schemas per tenant |
| Agents | Structured Pydantic models + deterministic scoring | LangGraph cycles, multi-agent swarms, tool calling |
| UI | One page that shows registration → audit → scored modules | Full marketplace, workflow builder, monitoring dashboard |
| Integrations | Stubs or mock responses for WhatsApp / CRM | Live API keys, n8n runtime, production credentials |
| Scoring | Transparent rules + small LLM explanation only when asked | Black-box LLM scoring presented as fact |

## Next Minimal Increments (in order)

1. Persist agencies and audits to local Postgres (docker-compose already present).
2. Replace pure in-memory scoring with a stored opportunity record.
3. Add one synthetic agency seed script.
4. Wire a single "approve modules" button that stores the selection.
5. Generate a simple text roadmap from the top modules (no PDF yet).

## References

- Module list and domains live in the original technical specification (21 modules across Growth / Sales / Operations).
- High-value infrastructure notes are in the project `docs/tech-registry-analysis.md` (mem0, Langfuse, n8n-mcp, deepeval, Playwright).
- Schema outline: `migrations/001_core_schema.sql`.

## Common Issues

| Symptom | Fix |
|---------|-----|
| Request to "add full multi-tenancy now" | Defer; keep single-tenant path and note the design decision |
| Desire to generate n8n workflows immediately | Stub the output; real generation is Phase 4 |
| Adding new LLM calls for every step | Prefer deterministic rules; use LLM only for natural-language summary |
| Scope creep into production monitoring | Capture the idea, return to the demo happy path |
