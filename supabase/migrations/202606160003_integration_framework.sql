create table if not exists public.integration_connections (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  provider text not null,
  source text not null,
  configured boolean not null default false,
  health text not null default 'not_configured',
  connected_at timestamptz,
  last_verified_at timestamptz,
  last_error text,
  config_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, provider, source)
);

create table if not exists public.sync_cursors (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  provider text not null,
  source text not null,
  cursor_key text not null,
  status text not null default 'idle',
  last_synced_at timestamptz,
  last_cursor text,
  records_seen integer not null default 0,
  records_processed integer not null default 0,
  last_error text,
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, provider, source, cursor_key)
);

create index if not exists idx_integration_connections_tenant_provider
  on public.integration_connections (tenant_id, provider, source);

create index if not exists idx_sync_cursors_tenant_provider
  on public.sync_cursors (tenant_id, provider, source, cursor_key);

alter table public.integration_connections enable row level security;
alter table public.sync_cursors enable row level security;

grant all privileges on public.integration_connections to authenticated;
grant all privileges on public.sync_cursors to authenticated;

create policy "tenant users read integration connections"
on public.integration_connections
for select
to authenticated
using (tenant_id = public.current_tenant_id());

create policy "admins manage integration connections"
on public.integration_connections
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

create policy "tenant users read sync cursors"
on public.sync_cursors
for select
to authenticated
using (tenant_id = public.current_tenant_id());

create policy "admins manage sync cursors"
on public.sync_cursors
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
