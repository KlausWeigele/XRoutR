def export_datev_bundle(invoice_id: str) -> dict:
    """Stub: create DATEV RDS/CSV bundle manifest for given invoice."""
    return {"invoice_id": invoice_id, "bundle_uri": f"s3://xroutr/datev/{invoice_id}.zip"}

