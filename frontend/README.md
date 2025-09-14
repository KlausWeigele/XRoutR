# Frontend (Next.js App Router)

Purpose
- Next.js App Router with BFF route handlers under `app/api/*`.

Conventions
- Server Components fetch via BFF; Client Components only for interactivity.
- Route Handlers default to Node runtime; set `export const runtime = 'nodejs'` when needed.
- Uploads via presigned S3; API receives metadata only.

Local Dev
- `pnpm dev` (requires Node 20 and env configured). See AGENTS.md sections 8 and 26.

