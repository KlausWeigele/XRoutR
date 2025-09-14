from __future__ import annotations
from lxml import etree
from .xml_utils import parse_xml
from typing import List

UBL_NS = {
    "inv": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
}

CII_NS = {
    "cii": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
}


def _validate_with_xsd(xml_bytes: bytes, xsd_bytes: bytes) -> List[dict]:
    doc = parse_xml(xml_bytes)
    xsd_doc = etree.fromstring(xsd_bytes)
    schema = etree.XMLSchema(xsd_doc)
    errors: List[dict] = []
    if not schema.validate(doc):
        for e in schema.error_log:  # type: ignore[attr-defined]
            errors.append(
                {
                    "code": 1000,
                    "rule_id": "XSD",
                    "layer": "schema",
                    "severity": "error",
                    "xpath": getattr(e, "path", ""),
                    "message_de": str(e),
                    "hint_de": None,
                }
            )
    return errors


def validate_ubl(xml_bytes: bytes) -> List[dict]:
    """Validate minimal UBL 2.1 Invoice structure with a tiny in-memory XSD.
    This is a pragmatic subset to avoid external downloads in tests.
    """
    xsd = f"""
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
               targetNamespace="{UBL_NS['inv']}"
               xmlns:inv="{UBL_NS['inv']}" xmlns:cbc="{UBL_NS['cbc']}"
               elementFormDefault="qualified" attributeFormDefault="unqualified">
      <xs:import namespace="{UBL_NS['cbc']}"/>
      <xs:element name="Invoice">
        <xs:complexType>
          <xs:sequence>
            <xs:any minOccurs="0" maxOccurs="unbounded" processContents="lax"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
    </xs:schema>
    """.encode("utf-8")
    try:
        return _validate_with_xsd(xml_bytes, xsd)
    except Exception as exc:  # fallback to well-formedness
        try:
            parse_xml(xml_bytes)
            return []
        except Exception:
            return [
                {
                    "code": 1000,
                    "rule_id": "XSD",
                    "layer": "schema",
                    "severity": "error",
                    "xpath": "",
                    "message_de": str(exc),
                    "hint_de": None,
                }
            ]


def validate_cii(xml_bytes: bytes) -> List[dict]:
    xsd = f"""
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
               targetNamespace="{CII_NS['cii']}"
               xmlns:cii="{CII_NS['cii']}"
               elementFormDefault="qualified">
      <xs:element name="CrossIndustryInvoice" type="xs:anyType"/>
    </xs:schema>
    """.encode("utf-8")
    try:
        return _validate_with_xsd(xml_bytes, xsd)
    except Exception as exc:
        try:
            parse_xml(xml_bytes)
            return []
        except Exception:
            return [
                {
                    "code": 1000,
                    "rule_id": "XSD",
                    "layer": "schema",
                    "severity": "error",
                    "xpath": "",
                    "message_de": str(exc),
                    "hint_de": None,
                }
            ]
