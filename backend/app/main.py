from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional
from prometheus_client import CollectorRegistry, Counter, generate_latest, CONTENT_TYPE_LATEST
from .tasks.validate_stub import perform_validation
from lxml import etree

from .models.canonical import CanonicalInvoice

app = FastAPI(title="XRoutR Backend", version="0.1.0")

registry = CollectorRegistry()
INGEST_TOTAL = Counter("invoices_ingested_total", "Invoices ingested", registry=registry, labelnames=("source",))
VALIDATED_TOTAL = Counter("invoices_validated_total", "Invoices validated", registry=registry, labelnames=("profile", "layer"))
VALIDATION_ERRORS_TOTAL = Counter("validation_errors_total", "Validation errors", registry=registry, labelnames=("layer", "rule_id"))


class IngestRequest(BaseModel):
    filename: Optional[str] = None
    content_type: Optional[str] = None
    s3_uri: Optional[str] = None
    tenant_id: Optional[str] = None


class IngestResponse(BaseModel):
    invoice_id: str
    job_id: str


# naive in-memory storage for demo/tests
STORAGE: dict[str, bytes] = {}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    data = generate_latest(registry)
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.post("/invoices/ingest", response_model=IngestResponse)
def invoices_ingest(req: IngestRequest):
    # For tests: accept s3_uri or inline xml in filename field (base64-unsafe avoided)
    xml = (req.filename or '').encode('utf-8') if req.s3_uri is None else b''
    invoice_id = "inv_00000001"
    job_id = "job_00000001"
    if xml:
        STORAGE[invoice_id] = xml
    INGEST_TOTAL.labels(source="api").inc()
    return IngestResponse(invoice_id=invoice_id, job_id=job_id)


@app.get("/invoices/{invoice_id}/validation")
def invoice_validation(invoice_id: str):
    xml = STORAGE.get(invoice_id)
    if not xml:
        # Fallback: simple minimal UBL for demo
        xml = b"""<Invoice xmlns=\"urn:oasis:names:specification:ubl:schema:xsd:Invoice-2\" xmlns:cbc=\"urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2\"></Invoice>"""
    findings = perform_validation(xml)
    for f in findings:
        VALIDATION_ERRORS_TOTAL.labels(layer=f.get("layer"), rule_id=f.get("rule_id")).inc()
    # naive profile label until detect_profile is exposed
    VALIDATED_TOTAL.labels(profile="xrechnung", layer="schema").inc()
    return {"invoice_id": invoice_id, "validation": findings}


@app.post("/invoices/{invoice_id}/route")
def invoice_route(invoice_id: str, target: str = Query("datev")):
    if target not in {"datev"}:
        raise HTTPException(status_code=400, detail="unsupported target")
    return {"invoice_id": invoice_id, "routed": True, "target": target}
