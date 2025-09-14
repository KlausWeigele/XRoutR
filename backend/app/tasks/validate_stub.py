from ..validation.xml_schema import validate_ubl, validate_cii
from ..validation.schematron_stub import run_schematron
from ..validation.svrl_parser_stub import svrl_to_findings
from ..validation.rules_engine import apply_catalog
from lxml import etree
import yaml
from pathlib import Path


def enqueue_validate(invoice_id: str, xml_ref: str) -> str:
    """Stub: enqueue validation job, return job id."""
    return "job_00000001"


def detect_profile(xml_bytes: bytes) -> str:
    root = etree.fromstring(xml_bytes)
    ns = root.nsmap.get(None) or root.tag.split('}')[0].strip('{')
    if ns.startswith('urn:oasis:names:specification:ubl'):
        return 'ubl'
    if ns.startswith('urn:un:unece:uncefact:data:standard:CrossIndustryInvoice'):
        return 'cii'
    return 'unknown'


def perform_validation(xml_bytes: bytes) -> list[dict]:
    profile = detect_profile(xml_bytes)
    issues: list[dict] = []
    # Schema layer
    if profile == 'ubl':
        issues += validate_ubl(xml_bytes)
    elif profile == 'cii':
        issues += validate_cii(xml_bytes)
    # Rules layer from catalog
    try:
        cat_path = Path(__file__).resolve().parents[3] / 'shared' / 'rules_catalog.yaml'
        catalog = yaml.safe_load(cat_path.read_text(encoding='utf-8')) or {}
    except Exception:
        catalog = {}
    doc = etree.fromstring(xml_bytes)
    issues += apply_catalog(doc, catalog)
    # Schematron facade (future)
    svrl = run_schematron(xml_bytes)
    issues += svrl_to_findings(svrl)
    # Deduplicate by (rule_id, layer, xpath, code)
    seen = set()
    deduped = []
    for it in issues:
        key = (it.get('rule_id'), it.get('layer'), it.get('xpath'), it.get('code'))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(it)
    return deduped
