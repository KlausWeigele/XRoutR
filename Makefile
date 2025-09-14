.PHONY: help dev test lint fmt validate-svrl export-datev openapi sbom

help:
	@echo "Targets:" && \
	echo "  dev               - start frontend/backend (stubs)" && \
	echo "  test              - run tests (stubs)" && \
	echo "  lint              - run linters (stubs)" && \
	echo "  fmt               - format code (stubs)" && \
	echo "  openapi           - export OpenAPI + gen TS types" && \
	echo "  validate-svrl     - validate fixtures vs goldens (stub)" && \
	echo "  export-datev      - build DATEV export bundle (stub)" && \
	echo "  sbom              - generate CycloneDX SBOMs (stub)"

dev:
	@echo "[stub] Run: cd frontend && pnpm dev | cd backend && uvicorn app.main:app --reload"

test:
	@echo "[stub] Run: pnpm test (frontend) and pytest (backend)"

lint:
	@echo "[stub] Run: pnpm lint && ruff check . && mypy"

fmt:
	@echo "[stub] Run: pnpm fmt && ruff format . && black ."

validate-svrl:
	@echo "[stub] Validate fixtures and compare to SVRL goldens"

export-datev:
	@echo "[stub] Produce DATEV RDS/CSV example bundle"

openapi:
	@echo "Export OpenAPI and generate TS types" && \
	python3 scripts/openapi_export.py && \
	cd frontend && npx openapi-typescript ../shared/openapi.json -o src/lib/api/types.ts

sbom:
	@echo "Generate SBOMs (CycloneDX)" && \
	(cd frontend && npx @cyclonedx/cyclonedx-npm --omit dev --output-file sbom-frontend.json) && \
	(cd backend && python3 -m pip install -q cyclonedx-bom && cyclonedx-py -o sbom-backend.json -F)
