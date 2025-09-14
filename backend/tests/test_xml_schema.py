from pathlib import Path
from app.validation.xml_schema import validate_ubl


def test_ubl_invalid_triggers_schema_error():
    bad = b"<NotInvoice/>"
    findings = validate_ubl(bad)
    assert any(f["layer"] == "schema" and 1000 <= f["code"] < 2000 for f in findings)
