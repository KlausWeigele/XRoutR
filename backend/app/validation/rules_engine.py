from __future__ import annotations
from lxml import etree
from typing import Dict, List, Any
import re
from .xml_utils import parse_xml

UBL_NS = {
    "inv": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
}


def _text(n: Any) -> str:
    if isinstance(n, etree._Element):
        return ("".join(n.itertext()) or "").strip()
    return str(n).strip()


def _predicate_ok(nodes: List[Any], predicate: Any) -> bool:
    if not predicate or predicate == "exists":
        return len(nodes) > 0
    if predicate == "notEmpty":
        return any(len(_text(n)) > 0 for n in nodes)
    if isinstance(predicate, dict):
        if "matches" in predicate:
            pat = re.compile(predicate["matches"])  # nosec
            return any(bool(pat.search(_text(n))) for n in nodes)
        if "enum" in predicate:
            allowed = set(map(str, predicate["enum"]))
            return any(_text(n) in allowed for n in nodes)
        if "minLength" in predicate:
            return all(len(_text(n)) >= int(predicate["minLength"]) for n in nodes)
        if "maxLength" in predicate:
            return all(len(_text(n)) <= int(predicate["maxLength"]) for n in nodes)
        if "number" in predicate and predicate["number"] is True:
            def is_num(s: str) -> bool:
                try:
                    float(s)
                    return True
                except Exception:
                    return False
            return all(is_num(_text(n)) for n in nodes)
        if "date" in predicate and predicate["date"] is True:
            # simple ISO date YYYY-MM-DD
            pat = re.compile(r"^\d{4}-\d{2}-\d{2}$")
            return all(bool(pat.match(_text(n))) for n in nodes)
    return False


def apply_catalog(xml_doc: etree._Element, catalog: Dict) -> List[dict]:
    findings: List[dict] = []
    # Merge both namespaces if needed; for now focus UBL
    nsmap = UBL_NS
    for layer in ("en16931", "xrechnung"):
        rules = catalog.get(layer, {}) or {}
        for rule_id, meta in rules.items():
            xpath = meta.get("xpath")
            severity = meta.get("severity", "error")
            message_de = meta.get("message_de", rule_id)
            hint_de = meta.get("hint_de")
            predicate = meta.get("predicate")
            if not xpath:
                continue
            nodes = xml_doc.xpath(xpath, namespaces=nsmap)
            ok = _predicate_ok(nodes, predicate)
            if not ok:
                code = 2000 if layer == "en16931" else 3000
                findings.append(
                    {
                        "code": code,
                        "rule_id": rule_id,
                        "layer": layer,
                        "severity": severity,
                        "xpath": xpath,
                        "message_de": message_de,
                        "hint_de": hint_de,
                    }
                )
    return findings
