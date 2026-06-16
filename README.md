# MTOS

Monthly Touch Operating System is an AI-powered Account Management Operating System for agencies. This repository now contains the first executable production scaffold for the MTOS platform:

- React + Vite + TypeScript frontend
- FastAPI backend
- Supabase base schema and RLS migration
- Docker local runtime
- GitHub Actions CI
- Product and architecture documents

## Repository Layout

```text
.
├─ .trae/documents/              # Product + technical references for build workflow
├─ api/                          # FastAPI service and tests
├─ docs/                         # MTOS PRD, architecture, and phased build plan
├─ src/                          # React application
├─ supabase/migrations/          # Base MTOS schema and RLS policies
├─ Dockerfile.web
├─ docker-compose.yml
└─ .github/workflows/ci.yml
```

## Current Scope

This scaffold includes:

- MTOS command center UI shell
- Client 360, Monthly Touches, Prompt Center, and Settings routes
- Typed MTOS API endpoints with mock operational data
- Base Supabase schema for tenants, ownership, Monthly Touches, prompts, and audit logs
- Ownership-oriented RLS policy scaffolding
- Frontend and backend test coverage for the initial slice

## Local Development

### Frontend

```bash
npm install
npm run dev
```

### Backend

```bash
cd api
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload --port 8000
```

If local port `8000` is already in use, run the API on `8001` and set `VITE_API_BASE_URL=http://localhost:8001`.

## Verification

Frontend:

```bash
npm run check
npm run test
npm run build
```

Backend:

```bash
cd api
py -m pytest
```

## Next Build Slices

The next recommended implementation steps are:

1. Replace mock API data with Supabase-backed repository services.
2. Implement ClickUp ownership sync and exception queue.
3. Build Monthly Touch brief generation workflow and prompt execution tracing.
4. Add auth context from Supabase Auth and enforce ownership across API queries.
5. Add job orchestration for pre-meeting intelligence, recap approval, and QA workflows.

## Supabase Repository Mode

The API supports a repository switch:

- `MTOS_REPOSITORY_MODE=in_memory` (default)
- `MTOS_REPOSITORY_MODE=supabase`

When using `supabase`, provide:

- `MTOS_SUPABASE_URL`
- `MTOS_SUPABASE_SERVICE_ROLE_KEY`
- optional `MTOS_SUPABASE_ANON_KEY` (recommended when calling PostgREST with user JWTs to enforce RLS)

To run Supabase mode without full frontend auth wired in, you can also pass:

- `X-MTOS-Tenant-User-Id` header (the `tenant_users.id` UUID) along with `X-MTOS-Role`

JWT tenant/role resolution supports either top-level claims (`tenant_id`, `app_role`) or `app_metadata.tenant_id` / `app_metadata.app_role` depending on how your Supabase tokens are configured.

Setup guide: `docs/supabase-setup.md`

## Seeding Supabase (Dev)

If you want the current UI to run against Supabase immediately (before wiring real Supabase Auth in the frontend), you can seed deterministic demo rows using the service role key:

```bash
cd api
py scripts/seed_supabase.py
```

Then set these in your web `.env.local` so the demo identities can pass `X-MTOS-Tenant-User-Id`:

- `VITE_DEMO_TENANT_USER_ID_ADMIN=22222222-2222-2222-2222-222222222222`
- `VITE_DEMO_TENANT_USER_ID_AM1=33333333-3333-3333-3333-333333333333`
- `VITE_DEMO_TENANT_USER_ID_AM2=44444444-4444-4444-4444-444444444444`
