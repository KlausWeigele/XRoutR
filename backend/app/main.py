from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from prometheus_client import CollectorRegistry, Counter, generate_latest, CONTENT_TYPE_LATEST

from .models.canonical import CanonicalInvoice

app = FastAPI(title="XRoutR Backend", version="0.1.0")

registry = CollectorRegistry()
INGEST_TOTAL = Counter("invoices_ingested_total", "Invoices ingested", registry=registry, labelnames=("source",))
VALIDATED_TOTAL = Counter("invoices_validated_total", "Invoices validated", registry=registry, labelnames=("profile", "layer"))


class IngestRequest(BaseModel):
    filename: str | None = None
    content_type: str | None = None
    s3_uri: str | None = None
    tenant_id: str | None = None


class IngestResponse(BaseModel):
    invoice_id: str
    job_id: str


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    data = generate_latest(registry)
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.post("/invoices/ingest", response_model=IngestResponse)
def invoices_ingest(req: IngestRequest):
    # Stub: compute deterministic ids for now
    invoice_id = "inv_00000001"
    job_id = "job_00000001"
    INGEST_TOTAL.labels(source="api").inc()
    return IngestResponse(invoice_id=invoice_id, job_id=job_id)


@app.get("/invoices/{invoice_id}/validation")
def invoice_validation(invoice_id: str):
    # Stub: return minimal validation structure
    VALIDATED_TOTAL.labels(profile="xrechnung", layer="schema").inc()
    return {
        "invoice_id": invoice_id,
        "validation": [
            {
                "rule_id": "BR-01",
                "layer": "en16931",
                "severity": "error",
                "xpath": "//cbc:ID",
                "message_de": "Pflichtfeld BT-1 (Rechnungsnummer) ist leer.",
                "hint_de": "Tragen Sie eine eindeutige Rechnungsnummer ein.",
            }
        ],
    }


@app.post("/invoices/{invoice_id}/route")
def invoice_route(invoice_id: str, target: str = Query("datev")):
    if target not in {"datev"}:
        raise HTTPException(status_code=400, detail="unsupported target")
    return {"invoice_id": invoice_id, "routed": True, "target": target}

