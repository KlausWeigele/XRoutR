import time
import pytest
from app.main import app, STORAGE
from fastapi.testclient import TestClient


client = TestClient(app)


@pytest.mark.performance
def test_validation_p95_under_2s_three_runs():
    # Prepare minimal UBL without heavy processing
    xml = (
        b"<Invoice xmlns=\"urn:oasis:names:specification:ubl:schema:xsd:Invoice-2\" "
        b"xmlns:cbc=\"urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2\">"
        b"<cbc:ID>INV-3</cbc:ID>"
        b"</Invoice>"
    )
    STORAGE["inv_perf"] = xml
    durations = []
    for _ in range(3):
        t0 = time.time()
        r = client.get("/invoices/inv_perf/validation")
        assert r.status_code == 200
        durations.append((time.time() - t0) * 1000.0)
    for d in durations:
        assert d < 2000.0

