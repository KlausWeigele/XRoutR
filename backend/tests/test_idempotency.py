from app.main import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_ingest_idempotency_same_response():
    payload = {"filename": "<Invoice/>"}
    r1 = client.post("/invoices/ingest", json=payload, headers={"Idempotency-Key": "abc"})
    r2 = client.post("/invoices/ingest", json=payload, headers={"Idempotency-Key": "abc"})
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json() == r2.json()


def test_ingest_idempotency_fallback_same_within_minute(monkeypatch):
    # Same payload without header should dedupe within the same minute window
    payload = {"filename": "<Invoice/>", "tenant_id": "t-1"}
    r1 = client.post("/invoices/ingest", json=payload)
    r2 = client.post("/invoices/ingest", json=payload)
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json() == r2.json()
