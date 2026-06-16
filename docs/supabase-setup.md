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

## 4. Configure Web (Optional Demo Headers)

Set these in the repo root `.env.local`:

- `VITE_DEMO_TENANT_USER_ID_ADMIN=22222222-2222-2222-2222-222222222222`
- `VITE_DEMO_TENANT_USER_ID_AM1=33333333-3333-3333-3333-333333333333`
- `VITE_DEMO_TENANT_USER_ID_AM2=44444444-4444-4444-4444-444444444444`

Restart `npm run dev` after changing env vars.
