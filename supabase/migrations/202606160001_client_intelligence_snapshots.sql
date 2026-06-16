create table if not exists public.client_intelligence_snapshots (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  client_id uuid not null,
  source text not null default 'clickup',
  sync_status text not null check (sync_status in ('connected', 'warning', 'not_found')),
  clickup_task_id text,
  clickup_task_name text,
  clickup_task_url text,
  account_manager text,
  task_status text,
  task_priority text,
  due_at timestamptz,
  last_activity_at timestamptz,
  summary text not null,
  signals_json jsonb not null default '[]'::jsonb,
  synced_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

create unique index if not exists idx_client_intelligence_snapshot_unique
on public.client_intelligence_snapshots (tenant_id, client_id, source);

create index if not exists idx_client_intelligence_snapshot_lookup
on public.client_intelligence_snapshots (tenant_id, client_id, synced_at desc);

alter table public.client_intelligence_snapshots enable row level security;

grant all privileges on public.client_intelligence_snapshots to authenticated;

create policy "tenant users can read intelligence snapshots"
on public.client_intelligence_snapshots
for select
to authenticated
using (tenant_id = public.current_tenant_id());
