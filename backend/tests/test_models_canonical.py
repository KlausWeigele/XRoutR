from app.models.canonical import CanonicalInvoice, Header, Party, Line, VAT


def test_canonical_model_minimal():
    invoice = CanonicalInvoice(
        header=Header(invoice_id="INV-1", issue_date="2025-01-01", currency="EUR"),
        seller=Party(name="S", address={"city": "Berlin"}),
        buyer=Party(name="B", address={"city": "Berlin"}),
        lines=[Line(description="X", quantity=1, unit="EA", price=100.0, vat=VAT(category="S", rate=19.0), line_total=119.0)],
    )
    assert invoice.header.invoice_id == "INV-1"

