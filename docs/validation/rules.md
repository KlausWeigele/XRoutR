# Validierungsregeln (Beispiele)

## BR-01 — Rechnungsnummer fehlt
- XPath: `//cbc:ID`
- Beschreibung: Pflichtfeld BT‑1 ist leer.
- Korrektur: Tragen Sie eine eindeutige Rechnungsnummer in `cbc:ID` ein.

## XR-LEITWEG — Leitweg-ID fehlt (B2G)
- XPath: `//cbc:EndpointID`
- Beschreibung: Für B2G‑Rechnungen ist eine Leitweg‑ID erforderlich.
- Korrektur: Fügen Sie `cbc:EndpointID` mit korrektem Scheme ein.
