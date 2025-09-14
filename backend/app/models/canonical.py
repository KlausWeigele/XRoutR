from pydantic import BaseModel, Field
from typing import Optional, List


class Totals(BaseModel):
    net: float
    tax: float
    gross: float


class Header(BaseModel):
    invoice_id: str
    issue_date: str
    currency: str
    profile_id: Optional[str] = None
    customization_id: Optional[str] = None
    totals: Optional[Totals] = None


class Party(BaseModel):
    name: str
    vat_id: Optional[str] = None
    tax_id: Optional[str] = None
    address: dict


class VAT(BaseModel):
    category: str
    rate: float


class Line(BaseModel):
    description: str
    quantity: float
    unit: str
    price: float
    vat: VAT
    line_total: float


class TaxItem(BaseModel):
    category: str
    rate: float
    base: float
    amount: float


class Payment(BaseModel):
    payment_means: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    terms: Optional[str] = None
    due_date: Optional[str] = None


class References(BaseModel):
    order_ref: Optional[str] = None
    delivery_note: Optional[str] = None
    contract: Optional[str] = None


class Attachment(BaseModel):
    type: str
    uri: str
    hash: str


class ValidationEntry(BaseModel):
    code: int
    rule_id: str
    layer: str
    severity: str
    xpath: str
    message_de: str
    hint_de: Optional[str] = None


class CanonicalInvoice(BaseModel):
    header: Header
    seller: Party
    buyer: Party
    b2g: Optional[dict] = None
    lines: List[Line]
    tax: Optional[List[TaxItem]] = None
    payment: Optional[Payment] = None
    references: Optional[References] = None
    attachments: Optional[List[Attachment]] = None
    validation: Optional[List[ValidationEntry]] = None
