from ..validation.xml_schema_stub import validate_xml_schema
from ..validation.schematron_stub import run_schematron
from ..validation.svrl_parser_stub import svrl_to_findings


def enqueue_validate(invoice_id: str, xml_ref: str) -> str:
    """Stub: enqueue validation job, return job id."""
    return "job_00000001"


def perform_validation(xml_bytes: bytes) -> list[dict]:
    issues = validate_xml_schema(xml_bytes)
    svrl = run_schematron(xml_bytes)
    issues += svrl_to_findings(svrl)
    return issues

