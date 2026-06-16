create table if not exists public.ownership_sync_runs (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  provider text not null,
  source text not null,
  cadence_minutes integer not null default 15,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  matched_clients integer not null default 0,
  unmatched_clients integer not null default 0,
  status text not null default 'completed',
  metadata_json jsonb not null default '{}'::jsonb
);

create table if not exists public.ownership_sync_exceptions (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  run_id uuid,
  client_name text not null,
  external_account_manager text not null,
  suggested_user_name text,
  reason text not null,
  status text not null default 'open',
  last_seen_at timestamptz not null default now(),
  resolved_at timestamptz,
  resolved_by uuid,
  metadata_json jsonb not null default '{}'::jsonb
);

create index if not exists idx_ownership_sync_runs_tenant_started on public.ownership_sync_runs (tenant_id, started_at desc);
create index if not exists idx_ownership_sync_exceptions_tenant_status on public.ownership_sync_exceptions (tenant_id, status, last_seen_at desc);

alter table public.ownership_sync_runs enable row level security;
alter table public.ownership_sync_exceptions enable row level security;

grant all privileges on public.ownership_sync_runs to authenticated;
grant all privileges on public.ownership_sync_exceptions to authenticated;

create policy "admins read ownership sync runs"
on public.ownership_sync_runs
for select
to authenticated
using (
  tenant_id = public.current_tenant_id()
  and public.current_app_role() = 'admin'
);

create policy "admins manage ownership sync runs"
on public.ownership_sync_runs
for all
to authenticated
using (
  tenant_id = public.current_tenant_id()
  and public.current_app_role() = 'admin'
)
with check (
  tenant_id = public.current_tenant_id()
  and public.current_app_role() = 'admin'
);

create policy "admins read ownership sync exceptions"
on public.ownership_sync_exceptions
for select
to authenticated
using (
  tenant_id = public.current_tenant_id()
  and public.current_app_role() = 'admin'
);

create policy "admins manage ownership sync exceptions"
on public.ownership_sync_exceptions
for all
to authenticated
using (
  tenant_id = public.current_tenant_id()
  and public.current_app_role() = 'admin'
)
with check (
  tenant_id = public.current_tenant_id()
  and public.current_app_role() = 'admin'
);

