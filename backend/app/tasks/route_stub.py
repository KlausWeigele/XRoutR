from ..exporters.datev_stub import export_datev_bundle


def enqueue_route(invoice_id: str, target: str) -> str:
    return "job_00000002"


def perform_route(invoice_id: str, target: str) -> dict:
    if target == "datev":
        return export_datev_bundle(invoice_id)
    raise ValueError("unsupported target")

