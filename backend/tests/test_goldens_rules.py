from pathlib import Path
from lxml import etree
import json
from app.validation.rules_engine import apply_catalog
import yaml


def test_goldens_match_catalog_findings():
    root = Path(__file__).resolve().parents[2]
    catalog = yaml.safe_load((root / 'shared' / 'rules_catalog.yaml').read_text(encoding='utf-8'))

    # BR-01 missing id
    xml1 = (root / 'fixtures' / 'fail' / 'br-01-missing-id.xml').read_bytes()
    f1 = apply_catalog(etree.fromstring(xml1), catalog)
    expected1 = json.loads((root / 'fixtures' / 'expected' / 'br-01.json').read_text(encoding='utf-8'))
    for exp in expected1:
        assert exp in f1

    # XR-LEITWEG missing
    xml2 = (root / 'fixtures' / 'fail' / 'xr-leitweg-missing.xml').read_bytes()
    f2 = apply_catalog(etree.fromstring(xml2), catalog)
    expected2 = json.loads((root / 'fixtures' / 'expected' / 'xr-leitweg.json').read_text(encoding='utf-8'))
    for exp in expected2:
        assert exp in f2

