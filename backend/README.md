# Backend (FastAPI + Workers + Exporters)

Purpose
- Orchestrates validation (Schema → EN16931 → XRechnung), routing, exports, and archival.

Conventions
- Python 3.11, FastAPI; lxml/xmlschema; XSLT/Schematron.
- Workers via RQ/Celery; DLQ for routing errors.
- Immutable audit trail with SVRL artifacts.

Local Dev
- `uvicorn app.main:app --reload` (or `uv` runner). See AGENTS.md sections 2, 19, 26.

