# Fixtures (Pass/Fail Invoices & SVRL Goldens)

Layout
- `/fixtures/{pass|fail}/{format}/{profile}/...` e.g., `fail/ubl/xrechnung-3.0/`
- Files: `pass_*.xml`, `fail_*.xml`; goldens: `.svrl.xml` alongside.

Conventions
- Keep fixtures deterministic (sorting, timestamps fixed). See AGENTS.md section 17.

