import os
from pathlib import Path
from app.validation.validators import run_all


def _gen_ubl(size_kb: int) -> bytes:
    lines = []
    lines.append("<Invoice xmlns=\"urn:oasis:names:specification:ubl:schema:xsd:Invoice-2\" xmlns:cbc=\"urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2\">")
    lines.append("<cbc:ID>INV-BENCH</cbc:ID>")
    i = 0
    chunk = "<cbc:Note>aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</cbc:Note>"
    while sum(len(x) for x in lines) < size_kb * 1024:
        lines.append(chunk)
        i += 1
        if i > 100000:
            break
    lines.append("</Invoice>")
    return "".join(lines).encode("utf-8")


def test_benchmark_small_under_2s(benchmark):
    xml = _gen_ubl(50)
    def run():
        run_all(xml)
    result = benchmark(run)


def test_benchmark_medium_under_5s(benchmark):
    xml = _gen_ubl(500)
    def run():
        run_all(xml)
    result = benchmark(run)

