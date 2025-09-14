from __future__ import annotations
from typing import Dict, Tuple
from lxml import etree
from .xml_schema import validate_ubl, validate_cii
from .rules_engine import apply_catalog
from .schematron_stub import run_schematron
from .svrl_parser_stub import svrl_to_findings
from pathlib import Path
import yaml


def detect_profile(xml_bytes: bytes) -> Dict[str, str]:
    root = etree.fromstring(xml_bytes)
    ns = root.nsmap.get(None) or root.tag.split('}')[0].strip('{')
    if ns.startswith('urn:oasis:names:specification:ubl'):
        return {"profile_id": "ubl", "customization_id": "xrechnung"}
    if ns.startswith('urn:un:unece:uncefact:data:standard:CrossIndustryInvoice'):
        return {"profile_id": "cii", "customization_id": "xrechnung"}
    return {"profile_id": "unknown", "customization_id": ""}


def run_all(xml_bytes: bytes) -> Dict:
    meta = detect_profile(xml_bytes)
    validation: list[dict] = []
    # Schema
    if meta["profile_id"] == "ubl":
        validation += validate_ubl(xml_bytes)
    elif meta["profile_id"] == "cii":
        validation += validate_cii(xml_bytes)
    # Rules via catalog
    try:
        cat_path = Path(__file__).resolve().parents[3] / 'shared' / 'rules_catalog.yaml'
        catalog = yaml.safe_load(cat_path.read_text(encoding='utf-8')) or {}
    except Exception:
        catalog = {}
    doc = etree.fromstring(xml_bytes)
    validation += apply_catalog(doc, catalog)
    # Schematron facade
    svrl = run_schematron(xml_bytes)
    validation += svrl_to_findings(svrl)
    # Dedup
    seen = set()
    deduped = []
    for it in validation:
        key = (it.get('rule_id'), it.get('layer'), it.get('xpath'), it.get('code'))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(it)
    return {"profile": meta, "validation": deduped}

