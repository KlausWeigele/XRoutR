import time
from app.main import app, STORAGE
from fastapi.testclient import TestClient


client = TestClient(app)


def test_api_validation_deterministic_and_fast():
    # load fixture into storage like a prior ingest
    xml = b"""<Invoice xmlns=\"urn:oasis:names:specification:ubl:schema:xsd:Invoice-2\" xmlns:cbc=\"urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2\"></Invoice>"""
    STORAGE["inv_00000001"] = xml
    t0 = time.time()
    r = client.get("/invoices/inv_00000001/validation")
    dt = (time.time() - t0) * 1000
    assert r.status_code == 200
    payload = r.json()
    assert payload["invoice_id"] == "inv_00000001"
    assert isinstance(payload["validation"], list)
    # p95 budget proxy: ensure single run < 2000ms
    assert dt < 2000

