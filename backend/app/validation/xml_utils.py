from __future__ import annotations
import os
from typing import Optional
from lxml import etree


def safe_xml_parser() -> etree.XMLParser:
    return etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        dtd_validation=False,
        load_dtd=False,
        huge_tree=False,
        recover=False,
    )


def parse_xml(xml_bytes: bytes, max_bytes: Optional[int] = None) -> etree._Element:
    if max_bytes is None:
        max_bytes = int(os.getenv("MAX_XML_BYTES", str(10 * 1024 * 1024)))  # 10 MiB default
    if len(xml_bytes) > max_bytes:
        raise ValueError("XML exceeds maximum allowed size")
    # naive pre-scan to block DTD/entities
    head = xml_bytes[:4096].lstrip()
    if b"<!DOCTYPE" in head or b"<!ENTITY" in head:
        raise ValueError("Prohibited DOCTYPE/ENTITY in XML")
    parser = safe_xml_parser()
    return etree.fromstring(xml_bytes, parser=parser)

