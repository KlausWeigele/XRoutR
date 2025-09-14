"""
Export FastAPI OpenAPI schema to shared/openapi.json
AGENTS.md §6, §5 BFF typed client
"""

from pathlib import Path
import json


def main() -> None:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
    from app.main import app  # type: ignore

    schema = app.openapi()
    # Ensure /metrics not present (include_in_schema=False in app)
    out = Path(__file__).resolve().parents[1] / "shared" / "openapi.json"
    out.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
