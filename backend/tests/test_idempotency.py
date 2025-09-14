from app.main import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_ingest_idempotency_same_response():
    payload = {"filename": "<Invoice/>"}
    r1 = client.post("/invoices/ingest", json=payload, headers={"Idempotency-Key": "abc"})
    r2 = client.post("/invoices/ingest", json=payload, headers={"Idempotency-Key": "abc"})
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json() == r2.json()

