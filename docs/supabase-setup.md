# Supabase Setup (MTOS Dev)

## 1. Apply Database Migrations

Run the SQL files in this order in the Supabase SQL Editor:

1. `supabase/migrations/202606150001_mtos_base.sql`
2. `supabase/migrations/202606150002_ownership_sync.sql`
3. `supabase/migrations/202606150003_update_auth_claims.sql`
4. `supabase/migrations/202606150004_ui_scaffold_fields.sql`

Notes:

- The seed script and Supabase repository mode assume these tables and columns exist.
- If you already applied an earlier version, re-running should be safe because the migrations use `if not exists` where appropriate.

## 2. Seed Demo Data

From `d:\m.t.o.s1\api`:

```bash
py scripts/seed_supabase.py
```

## 3. Configure API

Set these in `.env.local` (repo root) or `api/.env`:

- `MTOS_REPOSITORY_MODE=supabase`
- `MTOS_SUPABASE_URL=...`
- `MTOS_SUPABASE_SERVICE_ROLE_KEY=...`
- `MTOS_SUPABASE_ANON_KEY=...` (recommended)

## 4. Configure Seed Tenant

Set these in the repo root `.env.local` before running the seed:

- `MTOS_SEED_TENANT_ID=<tenant-uuid>`
- `MTOS_SEED_TENANT_NAME=<tenant-name>`
- `MTOS_SEED_TENANT_SLUG=<tenant-slug>`

Restart `npm run dev` after changing env vars.

The web app no longer uses demo tenant headers. Authenticate with Supabase Auth and ensure each user has a matching `tenant_users` row.

## 5. Verify In App

Open the Settings page in MTOS and review:

- Runtime Status
- System Checks
- Ownership Sync

The runtime panel will tell you whether MTOS is still using `in_memory` mode, whether Supabase credentials are loaded, and whether the required Supabase tables are reachable through PostgREST.
