from pathlib import Path
from lxml import etree
from app.validation.rules_engine import apply_catalog
import yaml


def load_catalog():
    root = Path(__file__).resolve().parents[2]
    return yaml.safe_load((root / 'shared' / 'rules_catalog.yaml').read_text(encoding='utf-8'))


def test_br01_and_xr_leitweg_rules_hit():
    root = Path(__file__).resolve().parents[2]
    xml = (root / 'fixtures' / 'fail' / 'br-01-missing-id.xml').read_bytes()
    doc = etree.fromstring(xml)
    cat = load_catalog()
    findings = apply_catalog(doc, cat)
    assert any(f["rule_id"] == "BR-01" and f["layer"] == "en16931" for f in findings)

    xml2 = (root / 'fixtures' / 'fail' / 'xr-leitweg-missing.xml').read_bytes()
    doc2 = etree.fromstring(xml2)
    findings2 = apply_catalog(doc2, cat)
    assert any(f["rule_id"] == "XR-LEITWEG" and f["layer"] == "xrechnung" for f in findings2)
