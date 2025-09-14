from ..validation.validators import run_all


def enqueue_validate(invoice_id: str, xml_ref: str) -> str:
    """Stub: enqueue validation job, return job id."""
    return "job_00000001"


def perform_validation(xml_bytes: bytes) -> list[dict]:
    return run_all(xml_bytes)["validation"]
