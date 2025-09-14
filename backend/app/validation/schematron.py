from __future__ import annotations
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional
from lxml import etree

try:
    from lxml import isoschematron
except Exception:  # pragma: no cover
    isoschematron = None  # type: ignore


@lru_cache(maxsize=4)
def compile_schematron(path: str) -> Optional["isoschematron.Schematron"]:
    if isoschematron is None:
        return None
    p = Path(path)
    if not p.exists():
        return None
    parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False, dtd_validation=False)
    doc = etree.parse(str(p), parser)
    return isoschematron.Schematron(doc, store_report=True)  # type: ignore


def find_artifacts() -> dict:
    # Resolve directory from env
    base = os.getenv("SCHEMATRON_DIR")
    lock = Path(__file__).resolve().parents[3] / "shared" / "standards.lock.json"
    paths = {}
    if base:
        paths["base"] = base
    if lock.exists():
        import json
        data = json.loads(lock.read_text(encoding="utf-8"))
        paths["en16931"] = data.get("en16931_schematron_path")
        paths["xrechnung"] = data.get("xrechnung_schematron_path")
    return paths


def run_schematron(doc: etree._Element) -> Optional[etree._ElementTree]:
    if isoschematron is None:
        return None
    paths = find_artifacts()
    for key in ("en16931", "xrechnung"):
        rel = paths.get(key)
        if not rel:
            continue
        base = paths.get("base", "")
        sch_path = os.path.join(base, rel) if base else rel
        sch = compile_schematron(sch_path)
        if sch is None:
            continue
        if sch.validate(doc):
            # Even when valid, report exists (successful-report); return anyway
            return sch.validation_report
        else:
            return sch.validation_report
    return None
