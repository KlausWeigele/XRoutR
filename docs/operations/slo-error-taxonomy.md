# SLOs & Error-Taxonomy (Kurzfassung)

- SLOs: API/BFF p95 ≤ 200 ms; Validation p95 ≤ 2 s; Availability 99.9%.
- Error-Codes:
  - 1xxx = Schema/XML (UBL/CII)
  - 2xxx = EN 16931
  - 3xxx = XRechnung CIUS
  - 4xxx = Routing/Export
  - 5xxx = Archiv/Storage

Jede Fehlermeldung enthält: `code`, `rule_id`, `layer`, `xpath`, `message_de`, `hint_de`.
