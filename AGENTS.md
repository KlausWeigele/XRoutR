# AGENTS.md — Operating Manual for "XRoutR" (Next.js + FastAPI)

_Last updated: 2025‑09‑14_

**Table of Contents**
- [0) Mission & Non‑Goals](#0-mission--non-goals)
- [1) Standards & Compliance Canon](#1-standards--compliance-canon)
- [1.1) Standards-Versionierung & Update-Prozess](#11-standards-versionierung--update-prozess)
- [2) Architecture & Stack (Pinned)](#2-architecture--stack-pinned)
- [3) Canonical Data Contracts](#3-canonical-data-contracts)
- [3.1) Rules-Katalog (Schema & Beispiel)](#31-rules-katalog-schema--beispiel)
- [4) Security & Privacy](#4-security--privacy)
- [5) Roles (Multi‑Agent)](#5-roles-multiagent)
- [6) Working Agreements & Quality Gates](#6-working-agreements--quality-gates)
- [7) Repo Layout (Monorepo)](#7-repo-layout-monorepo)
- [8) Next.js Conventions](#8-nextjs-conventions)
- [9) LLM Usage Policy](#9-llm-usage-policy)
- [10) Task Ritual (PLAN → RESULTS → NEXT → RISKS)](#10-task-ritual-plan--results--next--risks)
- [11) Env & Secrets](#11-env--secrets)
- [12) Acceptance (V1)](#12-acceptance-v1)
- [13) Docs](#13-docs)
- [14) Scope & Instruction Precedence](#14-scope--instruction-precedence)
- [15) Versions & Tooling (Pinned)](#15-versions--tooling-pinned)
- [16) Commands Cheatsheet](#16-commands-cheatsheet)
- [17) Test/Fixtures Conventions](#17-testfixtures-conventions)
- [18) BFF/Proxy Policy](#18-bffproxy-policy)
- [19) Observability Contract](#19-observability-contract)
- [20) Secrets & Retention](#20-secrets--retention)
- [21) Canonical Schema Versioning](#21-canonical-schema-versioning)
- [22) IMAP Ingest Policy](#22-imap-ingest-policy)
- [23) LLM Prompting Skeleton](#23-llm-prompting-skeleton)
- [24) Security & Threat Model (Brief)](#24-security--threat-model-brief)
- [25) Accessibility & i18n](#25-accessibility--i18n)
- [26) Local Dev Quickstart](#26-local-dev-quickstart)
- [27) Operational SLO/SLAs & Error Taxonomy](#27-operational-sloslas--error-taxonomy)

> Always-on constraints executed before every task.  
> Scope: E‑Rechnung Router & Validator (EN 16931, XRechnung CIUS DE, ZUGFeRD/Factur‑X), DATEV Export, IMAP/Upload ingest; optional Peppol via partner AP.

## 0) Mission & Non‑Goals
- **Mission (V1)**: Receive e-invoices (XRechnung UBL/CII, ZUGFeRD/Factur‑X PDF/A‑3+XML) → validate (Schema → EN16931 BR → XRechnung) → explain errors (DE) → route/export (DATEV RDS/CSV, SFTP, webhooks) → immutable archive (WORM).
- **Non‑Goals**: No legal/tax advice; no OCR-legalization of PDFs; no Peppol AP self-host (use partner); no portal scraping without contract.

## 1) Standards & Compliance Canon
- **Standards**: EN 16931 (BR rules, BT/BG), XRechnung CIUS 3.x (Schematron 2.x+), UBL 2.1, UN/CEFACT CII D16B, ZUGFeRD/Factur‑X ≥ 2.1 (PDF/A‑3+XML).  
- **Compliance guardrails**: DSGVO (minimize data, AV/TOMs), GoBD‑friendly archiving, retention default 10y (configurable legal hold).  
- **Business framing**: Germany‑first SMB, B2G Leitweg‑ID, DATEV hand-offs.

### 1.1) Standards-Versionierung & Update-Prozess
- Version Pinning: XRechnung CIUS, EN 16931 Schematron, UBL/CII Schemata und Peppol Artefakte sind explizit versioniert in `/shared/standards.lock.json`.  
- Monthly Check: Automatischer Monatsjob prüft neue Releases und öffnet einen PR mit Changelog, Rules‑Diff und neuen Staging‑Fixtures.  
- Staging-Gates: (1) Alle Goldens grün, (2) Performance p95 unverändert, (3) Migrationshinweise in `/docs/upgrade/`.  
- Rollback-Plan: Standards auf letzte grüne Kombination revertierbar via `standards.lock.json`.

## 2) Architecture & Stack (Pinned)
- **Frontend (Next.js App Router)**: React 18+, TypeScript, **RSC**; **Auth.js** (passkeys + magic link); **next-intl** (de/en); **Tailwind + shadcn/ui**.  
- **BFF**: Next **Route Handlers** under `/app/api/*` → proxy to FastAPI; single auth boundary; SSR-friendly caching; no secrets in client.  
- **Typed Client**: Aus FastAPI‑OpenAPI generierter TypeScript‑Client (`openapi-typescript`) mit Zod‑Guards; Regeneration im CI Pflicht.  
- **Backend**: Python 3.11+ FastAPI; lxml/xmlschema; XSLT/Schematron; task queue (RQ/Celery).  
- **Data**: PostgreSQL (RLS), S3‑compatible storage (EU/DE) with **Object Lock (WORM)**; KMS encryption.  
- **Integrations**: IMAP/SMTP ingest; DATEV exports (RDS/CSV), SFTP; (V2) Peppol via partner AP.  
- **Observability**: Structured JSON logs, OpenTelemetry (optional), DLQ for routing; health endpoints; Kern‑Metriken gemäß Abschnitt 27.

## 3) Canonical Data Contracts
- **Canonical Invoice JSON**:  
  `header{invoice_id,issue_date,currency,profile_id,customization_id,totals{net,tax,gross}}`  
  `seller{ name, vat_id?, tax_id?, address{…} }`, `buyer{…}`, `b2g{leitweg_id?}`  
  `lines[]{ description, quantity, unit, price, vat{category,rate}, line_total }`  
  `tax[]{ category, rate, base, amount }` • `payment{payment_means, iban?, bic?, terms, due_date?}`  
  `references{order_ref?,delivery_note?,contract?}` • `attachments[]{type,uri,hash}`  
  `validation[]{rule_id,layer{schema|en16931|xrechnung},severity{error|warn},xpath,message_de,hint_de}`
- **I/O**: Upload XML or PDF/A‑3 (embedded XML). Return `invoice_id` + SVRL artifact link. Exports: DATEV RDS/CSV bundle + manifest; SFTP; signed archive ZIP.

### 3.1) Rules-Katalog (Schema & Beispiel)
- Datei: `/shared/rules_catalog.yaml`  
- Schema:  
  `en16931|xrechnung → { <RULE_ID>: { xpath, severity:error|warn, title, message_de, hint_de, doc_url } }`  
- Beispiel:
```yaml
en16931:
  BR-01:
    xpath: "//cbc:ID"
    severity: "error"
    title: "Rechnungsnummer fehlt"
    message_de: "Pflichtfeld BT-1 (Rechnungsnummer) ist leer."
    hint_de: "Tragen Sie eine eindeutige Rechnungsnummer in BT-1 (cbc:ID) ein."
    doc_url: "/docs/rules/en16931#br-01"
xrechnung:
  XR-LEITWEG:
    xpath: "//cbc:EndpointID"
    severity: "error"
    title: "Leitweg-ID fehlt (B2G)"
    message_de: "Für B2G-Receipts ist eine Leitweg-ID erforderlich."
    hint_de: "Fügen Sie die Leitweg-ID im Element cbc:EndpointID mit dem richtigen Scheme ein."
    doc_url: "/docs/rules/xrechnung#leitweg"
```

## 4) Security & Privacy
- **PII**: Minimize; redact IBAN/VAT IDs in logs; zero secret exposure to browser; secrets only server‑side.  
- **Tenant isolation**: Postgres RLS + S3 prefix per tenant.  
- **DSGVO**: AV contract, TOMs in `/docs/compliance`; export/delete flows respecting retention/legal hold.  
- **Audit**: Immutable audit trail (ingest/validation/routing) + SVRL artifacts; UTC timestamps.
- **Threat Model (Top 5)**: XXE, Zip‑Bomb/Polyglot‑PDF, ID‑Enumeration (Multi‑Tenant), Secret‑Leakage in Logs, S3‑Retention‑Bypass.  
- **Secrets Policy**: Rotation quartalsweise; KMS‑Key‑Backups; Break‑Glass‑Account (MFA, offline verwahrt) mit Runbook.

## 5) Roles (Multi‑Agent)
- **ARCHITECT** (ADRs, dependency policy, threat model)  
- **STANDARDS_VALIDATION** (Schema/Schematron, SVRL parser, fixtures)  
- **BACKEND_API** (FastAPI orchestration, exporters, workers)  
- **BFF_NEXT** (Route Handlers, auth integration, proxy policies, caching; typed TS‑Client aus OpenAPI in CI)  
- **FRONTEND_NEXT** (App Router pages, RSC data, client components, UI states)  
- **CONNECTORS_DATEV** (RDS/CSV mapping & packages)  
- **CONNECTORS_EMAIL** (IMAP/MIME, PDF/A‑3 XML extractor, quarantine)  
- **DEVOPS** (Docker/compose, CI, S3 object‑lock, backups)  
- **QA** (unit/property/e2e tests, golden SVRLs)  
- **DOCS_COMPLIANCE** (user/admin docs, AV/TOM templates, audit guide)

## 6) Working Agreements & Quality Gates
- **DoD**: Lint+type‑check clean; tests for happy/edge paths; docs updated; OpenAPI current; security checklist OK.  
- **Validation PRs**: Provide failing & passing fixtures + expected SVRL.  
 - **Idempotency/Dedupe**: `idempotency_key = sha256(file_hash + sender + received_at_floor_minute)`; gleiche Keys liefern identische Ergebnisse, Duplikate werden markiert statt erneut verarbeitet.  
- **Perf budgets**: Validation ≤ 2s p95; Next SSR route ≤ 200ms server time p95 (excluding network to backend).

## 7) Repo Layout (Monorepo)
- `/frontend` — Next.js app (App Router)
- `/backend` — FastAPI + workers + exporters
- `/shared` — Canonical schemas, types, `rules_catalog.yaml`
- `/fixtures` — Pass/Fail invoices & SVRL goldens
- `/docs` — MkDocs, ADRs, compliance (AV/TOMs)
- `/infra` — Docker, compose, env, runbooks
- `/scripts` — Tools (Schematron runner, data converters)

## 8) Next.js Conventions
- **App Router** only; no `/pages`.  
- **Route Handlers** under `/app/api/*` are **Node runtime** by default; set `export const runtime = 'nodejs'` explicitly when needed; keep heavy CPU elsewhere (Python).  
- **Server Components** fetch via BFF; **Client Components** only for interactivity.  
- **Uploads**: Prefer **presigned S3**; app/api receives metadata only.  
- **Middleware**: Tenant by hostname; light auth gate; no heavy logic at edge.  
- **i18n**: `next-intl`; default `de-DE`; `en` fallback.
 - **Cache-Policy Matrix**: Validation/Status `cache: 'no-store'`; Archive‑Listing `revalidate: 60`; Signed‑Downloads `Cache-Control: private, max-age=300`.  
 - **Uploads (Security)**: PDF/XML Content‑Type‑Whitelist; Größe < 10 MB hard limit (config); Quarantäne‑Bucket vor endgültigem Archiv.

## 9) LLM Usage Policy
- LLMs for **error explanations & scaffolding** only; conformance = deterministic via schema/schematron.  
- Always cite BR/XR rule ids; if unsure → mark unknown; do not invent rules.  
- Mask sensitive invoice fields in prompts.

## 10) Task Ritual (PLAN → RESULTS → NEXT → RISKS)
- Every task emits PLAN, then RESULTS, NEXT, RISKS. Prefer small diffs; Conventional Commits.

## 11) Env & Secrets
- **Frontend**: `AUTH_SECRET`, `NEXTAUTH_URL`, `NEXTAUTH_SECRET`, `S3_*`, `BFF_BACKEND_URL`, `NEXT_INTL_LOCALES`, `TENANT_SIGNING_KEY`.  
- **Backend**: `DATABASE_URL`, `S3_*`, `IMAP_*`, `SMTP_*`, `KMS_*`.  
- Never expose secrets via `NEXT_PUBLIC_*` unless truly public; safe defaults.
 - **CI/CD Guardrails**: GH Actions Stages — Lint/Typecheck → Tests (FE/BE) → Build → SBOM (CycloneDX) → License‑Scan → gitleaks Secret‑Scan.

## 12) Acceptance (V1)
- Valid XRechnung → no errors; DATEV bundle imports in test harness.  
- Missing BT field → BR error with correct rule id/xpath & German hint.  
- ZUGFeRD PDF/A‑3 → embedded XML extracted, validated, archived with hash.  
- Re‑ingest same email/file → duplicate detection; immutable audit log present.

## 13) Docs
- OpenAPI + Swagger; Quickstart, Validation rules (examples), Export guide, Archive/auditor access, AV/TOM templates.  
- UI embeds legal notice: “Technische Prüfungen nach EN16931/XRechnung. **Keine Rechts‑/Steuerberatung.**”

## 14) Scope & Instruction Precedence
- Apply in this order (highest first): `AGENTS.md` → directory `ADR` → directory `README` → inline code comments.  
- If a conflict exists, prefer stricter security/compliance guidance.  
- Changes to scope require an ADR and update of this file.

## 15) Versions & Tooling (Pinned)
- **Node**: 20.x (LTS) • **Package manager**: `pnpm` 9.x  
- **Next.js**: 14.x (App Router) • **TypeScript**: 5.x  
- **Python**: 3.11.x • **Poetry** or `uv` for locking  
- **Docker**: 24+ • **Compose spec**: v3.9  
- Enforce with `.tool-versions`/`volta` and lockfiles committed.

## 16) Commands Cheatsheet
- `make dev` — Start frontend/backend in watch mode (stubs if not present).  
- `make test` — Run unit/prop/e2e tests (frontend+backend).  
- `make lint` — Run linters/formatters (ts, py).  
- `make fmt` — Format all code.  
- `make validate-svrl` — Validate fixtures and compare to SVRL goldens.  
- `make export-datev` — Build DATEV example export bundle.

## 17) Test/Fixtures Conventions
- Structure: `/fixtures/{pass|fail}/{format}/{profile}/...` e.g., `fail/ubl/xrechnung-3.0/…`.  
- Names: `pass_*.xml`, `fail_*.xml`; include short slug of the key violated BT/BR.  
- Goldens: place SVRL under same path with `.svrl.xml`.  
- Determinism: sort nodes/attrs in processing; fix timestamps; compare ignoring non-semantic whitespace.  
- PRs: include one failing and one passing fixture per new rule.

## 18) BFF/Proxy Policy
- Timeout: 10s default; retries: 2 with exponential backoff (jitter).  
- Allowed headers upstream: `authorization`, `content-type`, `accept`, tenant scoping headers.  
- Auth: single boundary in BFF; no client secrets; JWT/session validation server-side.  
- Caching: tag-based revalidation; avoid caching PII; respect `Cache-Control` from backend only when marked safe.  
- Payload limits: uploads via presigned S3 only; API accepts metadata ≤ 64 KiB.

## 19) Observability Contract
- Log JSON lines with: `ts_utc`, `level`, `tenant_id`, `invoice_id?`, `corr_id`, `stage{ingest|validate|route|export}`, `latency_ms`, `msg`.  
- Redact: IBAN, VAT IDs, emails in logs; store hashes when needed.  
- Tracing: optional OpenTelemetry; propagate `traceparent` across BFF→Backend.  
- Metrics: validation latency p95/p99, queue depth, DLQ size, export success rate.  
- Alerts: DLQ > 0 for 5m; p95 validation > 2s for 10m.

## 20) Secrets & Retention
- Use `.env` files locally; in prod, use secret manager (no .env).  
- Object storage: enable Object Lock (WORM) with default retention 10 years; support legal hold.  
- Provide `.env.example` and never commit real secrets.  
- Avoid `NEXT_PUBLIC_*` unless strictly public and reviewed.

## 21) Canonical Schema Versioning
- SemVer for `shared/canonical-invoice.json` and mapping code.  
- Backward compatibility window: accept n and n-1 for 6 months.  
- Migrations: provide `scripts/migrate_canonical_v{n-1}_to_v{n}.py`.  
- Each version documented with examples under `/docs/canonical/{version}`.

## 22) IMAP Ingest Policy
- Only accept from allowlist domains; quarantine unknown senders.  
- Deduplication: SHA-256 over normalized XML payload or PDF embedded XML.  
- Strip tracking pixels; blocklist common malware extensions.  
- Quarantine reasons logged with `corr_id` and retention 30 days.

## 23) LLM Prompting Skeleton
- Purpose: Explain validation errors; never decide conformance.  
- Prompt template (inputs masked):  
  """
  System: Du bist ein EN16931/XRechnung Erklär‑Assistent. Antworte kurz, sachlich, auf Deutsch.
  Nutzer: Kontext {layer: schema|en16931|xrechnung, rule_id, xpath, svrl_snippet}
  Aufgabe: Erkläre den Fehler, nenne BR/XR‑ID wörtlich, gib 1–2 Korrekturhinweise. Wenn unklar, schreibe "Regel unbekannt".
  """
- Token budgets: ≤ 1k/input; redact IBAN/VAT/name fields.

## 24) Security & Threat Model (Brief)
- Trust boundaries: Browser ↔ BFF ↔ Backend ↔ Storage/Queue.  
- Threats (STRIDE): spoofing (session fixation), tampering (XML injection), repudiation (missing audit), info disclosure (PII logs), DoS (oversized files), elevation (RCE in XSLT).  
- Mitigations: Auth.js best practices, XML parsers with XXE disabled, immutable audit trail, redaction, size limits, sandboxed XSLT/Schematron, S3 Object Lock.

## 25) Accessibility & i18n
- WCAG 2.2 AA budget; keyboard access for all interactive UI.  
- Use semantic HTML; test with screen readers for key flows.  
- next-intl keys: no free text in components; all strings via catalog; DE default, EN fallback.

## 26) Local Dev Quickstart
- Requirements: Node 20.x with `pnpm`, Python 3.11, Docker Desktop.  
- Copy `.env.example` to local env files as needed.  
- Minimal flow:  
  - Frontend: `cd frontend && pnpm dev` (BFF routes stub initially)  
  - Backend: `cd backend && uv run fastapi dev` or `uvicorn app.main:app --reload`  
  - Validate: `make validate-svrl` compares fixtures to goldens (once implemented).

## 27) Operational SLO/SLAs & Error Taxonomy
- SLOs (internal):  
  - API/BFF p95 server time ≤ 200 ms (Validation‑Reads: no‑store).  
  - Validation‑Worker p95 ≤ 2 s, p99 ≤ 5 s pro Rechnung.  
  - Routing‑Job TTR ≤ 30 s p95 (DATEV‑Export erzeugt & persistiert).  
  - Availability 99.9% core API (rolling 30d).  
  - RPO ≤ 15 min, RTO ≤ 60 min.  
- Error Taxonomy (Codes & Mapping):  
  - 1xxx = Schema/XML (UBL/CII), 2xxx = EN 16931, 3xxx = XRechnung CIUS, 4xxx = Routing/Export, 5xxx = Archiv/Storage.  
  - Jedes Fehlerobjekt enthält: `code`, `rule_id?`, `layer`, `xpath`, `message_de`, `hint_de`, `doc_url`.  
  - Retry‑Policy: 1xxx/2xxx/3xxx keine Auto‑Retries; 4xxx/5xxx = Exponential Backoff (×3), dann DLQ.  
- Metrics (Prometheus/OpenTelemetry):  
  - `invoices_ingested_total{source}`, `invoices_validated_total{profile,layer}`, `validation_errors_total{layer,rule_id}`, `job_duration_seconds{type}`, `archive_worm_violations_total`.  
- Alarms: p95 Validation > 2 s (5 min), DLQ size > 10, Export‑Fehlerquote > 2% (15 min).
