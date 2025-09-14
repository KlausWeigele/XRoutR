# Validierungsregeln (Beispiele)

## BR-01 — Rechnungsnummer fehlt
- XPath: `//cbc:ID`
- Prädikat: `notEmpty`
- Beschreibung: Pflichtfeld BT‑1 (cbc:ID) ist leer.
- Korrektur: Eindeutige Nummer in `cbc:ID` (BT‑1) eintragen.

## XR-LEITWEG — Leitweg-ID fehlt (B2G)
- XPath: `//cbc:EndpointID`
- Prädikat: `exists`
- Beschreibung: Für B2G‑Rechnungen ist eine Leitweg‑ID erforderlich.
- Korrektur: `cbc:EndpointID` mit korrektem Scheme ergänzen.
