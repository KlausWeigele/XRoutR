from typing import List, Dict
from lxml import etree


def svrl_to_findings(svrl_xml: bytes) -> List[Dict]:
    """Parse SVRL failed-asserts into ValidationEntry dicts.
    Maps each failed-assert to {code, rule_id, layer, severity, xpath, message_de, hint_de}.
    layer is inferred if rule_id prefix contains 'BR-' (en16931) or 'XR-' (xrechnung), else 'en16931'.
    """
    ns = {"svrl": "http://purl.oclc.org/dsdl/svrl"}
    root = etree.fromstring(svrl_xml)
    findings: List[Dict] = []
    for fa in root.xpath("//svrl:failed-assert", namespaces=ns):
        rid = fa.get("id") or fa.get("flag") or "RULE"
        location = fa.get("location") or ""
        text_el = fa.find("svrl:text", namespaces=ns)
        text = (text_el.text or "").strip() if text_el is not None else ""
        layer = "xrechnung" if rid.startswith("XR-") else "en16931"
        code = 3000 if layer == "xrechnung" else 2000
        findings.append(
            {
                "code": code,
                "rule_id": rid,
                "layer": layer,
                "severity": "error",
                "xpath": location,
                "message_de": text,
                "hint_de": None,
            }
        )
    # Also map successful-report as informational finding (severity=warn)
    for sr in root.xpath("//svrl:successful-report", namespaces=ns):
        rid = sr.get("id") or sr.get("flag") or "RULE"
        location = sr.get("location") or ""
        text_el = sr.find("svrl:text", namespaces=ns)
        text = (text_el.text or "").strip() if text_el is not None else ""
        layer = "xrechnung" if rid.startswith("XR-") else "en16931"
        code = 3000 if layer == "xrechnung" else 2000
        findings.append(
            {
                "code": code,
                "rule_id": rid,
                "layer": layer,
                "severity": "warn",
                "xpath": location,
                "message_de": text,
                "hint_de": None,
            }
        )
    return findings
