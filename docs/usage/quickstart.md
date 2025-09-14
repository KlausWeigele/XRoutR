# Quickstart

- Anforderungen: Node 20, pnpm, Python 3.11, Docker.
- `.env.example` Dateien kopieren und anpassen.
- `make openapi` zum Export der OpenAPI und TS-Typen.
- `docker-compose -f infra/docker-compose.yml up --build` startet Stack.
- Frontend: http://localhost:3000 • Backend: http://localhost:8000/healthz
