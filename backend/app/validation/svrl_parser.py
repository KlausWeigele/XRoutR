from typing import List, Dict
from lxml import etree
from .xml_utils import safe_xml_parser


def svrl_to_findings(svrl_xml: bytes) -> List[Dict]:
    """Parse SVRL failed-asserts into ValidationEntry dicts.
    Maps each failed-assert to {code, rule_id, layer, severity, xpath, message_de, hint_de}.
    layer is inferred if rule_id prefix contains 'BR-' (en16931) or 'XR-' (xrechnung), else 'en16931'.
    """
    ns = {"svrl": "http://purl.oclc.org/dsdl/svrl"}
    # Parse SVRL with hardened XML parser (no DTD/entities/network)
    root = etree.fromstring(svrl_xml, parser=safe_xml_parser())
    findings: List[Dict] = []
    for fa in root.xpath("//svrl:failed-assert|//svrl:successful-report", namespaces=ns):
        rid = fa.get("id") or fa.get("flag") or "RULE"
        location = fa.get("location") or ""
        text_el = fa.find("svrl:text", namespaces=ns)
        text = (text_el.text or "").strip() if text_el is not None else ""
        layer = "xrechnung" if rid.startswith("XR-") or rid.startswith("XRECHNUNG-") else "en16931"
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
    return findings
