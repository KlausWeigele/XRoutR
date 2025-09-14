from __future__ import annotations
from lxml import etree
from typing import Dict, List

UBL_NS = {
    "inv": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
}


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
            if not xpath:
                continue
            nodes = xml_doc.xpath(xpath, namespaces=nsmap)
            if len(nodes) == 0:
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

