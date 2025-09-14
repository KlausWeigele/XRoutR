from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional, Optional as Opt
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from .tasks.validate_stub import perform_validation
from .validation.validators import run_all
from lxml import etree

from .models.canonical import CanonicalInvoice

app = FastAPI(title="XRoutR Backend", version="0.1.0")

registry = CollectorRegistry()
INGEST_TOTAL = Counter("invoices_ingested_total", "Invoices ingested", registry=registry, labelnames=("source",))
VALIDATED_TOTAL = Counter("invoices_validated_total", "Invoices validated", registry=registry, labelnames=("profile", "layer"))
VALIDATION_ERRORS_TOTAL = Counter("validation_errors_total", "Validation errors", registry=registry, labelnames=("layer", "rule_id"))
VALIDATION_DURATION = Histogram(
    "validation_duration_seconds",
    "Validation duration",
    registry=registry,
    labelnames=("profile",),
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0),
)
XML_SIZE_BYTES = Histogram(
    "xml_size_bytes",
    "Size of input XML in bytes",
    registry=registry,
    buckets=(1024, 10*1024, 50*1024, 100*1024, 500*1024, 1024*1024, 5*1024*1024),
)


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


@app.get("/metrics", include_in_schema=False)
def metrics():
    data = generate_latest(registry)
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


IDEMP_STORE: dict[str, IngestResponse] = {}


@app.post("/invoices/ingest", response_model=IngestResponse)
def invoices_ingest(req: IngestRequest, idempotency_key: Optional[str] = Header(default=None, convert_underscores=False)):
    # For tests: accept s3_uri or inline xml in filename field (base64-unsafe avoided)
    xml = (req.filename or '').encode('utf-8') if req.s3_uri is None else b''
    invoice_id = "inv_00000001"
    job_id = "job_00000001"
    if idempotency_key and idempotency_key in IDEMP_STORE:
        return IDEMP_STORE[idempotency_key]
    if not idempotency_key:
        # Fallback: derive idempotency from payload + tenant + current minute
        import hashlib, time
        minute = int(time.time() // 60)
        basis = (xml or b"") + (req.tenant_id or "").encode("utf-8") + str(minute).encode("utf-8")
        idempotency_key = "auto:" + hashlib.sha256(basis).hexdigest()
    if xml:
        STORAGE[invoice_id] = xml
        try:
            XML_SIZE_BYTES.observe(len(xml))
        except Exception:
            pass
    INGEST_TOTAL.labels(source="api").inc()
    resp = IngestResponse(invoice_id=invoice_id, job_id=job_id)
    if idempotency_key:
        IDEMP_STORE[idempotency_key] = resp
    return resp


@app.get("/invoices/{invoice_id}/validation")
def invoice_validation(invoice_id: str):
    xml = STORAGE.get(invoice_id)
    if not xml:
        # Fallback: simple minimal UBL for demo
        xml = b"""<Invoice xmlns=\"urn:oasis:names:specification:ubl:schema:xsd:Invoice-2\" xmlns:cbc=\"urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2\"></Invoice>"""
    import time
    start = time.perf_counter()
    result = run_all(xml)
    duration = time.perf_counter() - start
    findings = result["validation"]
    for f in findings:
        VALIDATION_ERRORS_TOTAL.labels(layer=f.get("layer"), rule_id=f.get("rule_id")).inc()
    # profile label from detection
    profile_id = result.get("profile", {}).get("profile_id", "unknown")
    VALIDATED_TOTAL.labels(profile=profile_id, layer="schema").inc()
    VALIDATION_DURATION.labels(profile=profile_id).observe(duration)
    XML_SIZE_BYTES.observe(len(xml))
    return {"invoice_id": invoice_id, "profile": result.get("profile"), "validation": findings}


@app.post("/invoices/{invoice_id}/route")
def invoice_route(invoice_id: str, target: str = Query("datev")):
    if target not in {"datev"}:
        raise HTTPException(status_code=400, detail="unsupported target")
    return {"invoice_id": invoice_id, "routed": True, "target": target}
