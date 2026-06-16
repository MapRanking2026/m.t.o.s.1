create extension if not exists "pgcrypto";

create or replace function public.current_tenant_id()
returns uuid
language sql
stable
as $$
  select nullif(auth.jwt() ->> 'tenant_id', '')::uuid;
$$;

create or replace function public.current_app_role()
returns text
language sql
stable
as $$
  select coalesce(auth.jwt() ->> 'app_role', 'account_manager');
$$;

create table if not exists public.tenants (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text not null unique,
  status text not null default 'active',
  created_at timestamptz not null default now()
);

create table if not exists public.tenant_users (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  auth_user_id uuid not null,
  full_name text not null,
  role text not null check (role in ('admin', 'account_manager')),
  created_at timestamptz not null default now()
);

create table if not exists public.clients (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  external_ref text,
  name text not null,
  status text not null default 'active',
  timezone text,
  created_at timestamptz not null default now()
);

create table if not exists public.client_ownership (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  client_id uuid not null,
  user_id uuid not null,
  source text not null default 'clickup_sync',
  synced_at timestamptz not null default now(),
  active boolean not null default true
);

create table if not exists public.monthly_touches (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  client_id uuid not null,
  scheduled_at timestamptz not null,
  stage text not null,
  lookback_window_days integer not null default 30,
  created_at timestamptz not null default now()
);

create table if not exists public.prompt_templates (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid,
  category text not null,
  name text not null,
  status text not null default 'draft',
  created_at timestamptz not null default now()
);

create table if not exists public.prompt_versions (
  id uuid primary key default gen_random_uuid(),
  prompt_template_id uuid not null,
  version_number integer not null,
  system_prompt text not null,
  user_prompt text not null,
  config_json jsonb not null default '{}'::jsonb,
  is_active boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  actor_user_id uuid,
  action text not null,
  entity_type text not null,
  entity_id uuid,
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_tenant_users_tenant_auth on public.tenant_users (tenant_id, auth_user_id);
create index if not exists idx_clients_tenant on public.clients (tenant_id);
create index if not exists idx_client_ownership_client on public.client_ownership (tenant_id, client_id, active);
create index if not exists idx_monthly_touches_tenant_schedule on public.monthly_touches (tenant_id, scheduled_at desc);
create index if not exists idx_prompt_templates_category on public.prompt_templates (coalesce(tenant_id, '00000000-0000-0000-0000-000000000000'::uuid), category);

alter table public.tenants enable row level security;
alter table public.tenant_users enable row level security;
alter table public.clients enable row level security;
alter table public.client_ownership enable row level security;
alter table public.monthly_touches enable row level security;
alter table public.prompt_templates enable row level security;
alter table public.prompt_versions enable row level security;
alter table public.audit_logs enable row level security;

grant usage on schema public to anon, authenticated;
grant select on public.tenants to authenticated;
grant all privileges on public.tenant_users to authenticated;
grant all privileges on public.clients to authenticated;
grant all privileges on public.client_ownership to authenticated;
grant all privileges on public.monthly_touches to authenticated;
grant all privileges on public.prompt_templates to authenticated;
grant all privileges on public.prompt_versions to authenticated;
grant all privileges on public.audit_logs to authenticated;

create policy "tenant users can read their membership"
on public.tenant_users
for select
to authenticated
using (tenant_id = public.current_tenant_id());

create policy "tenant admins manage memberships"
on public.tenant_users
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

create policy "admins see all tenant clients"
on public.clients
for select
to authenticated
using (
  tenant_id = public.current_tenant_id()
  and public.current_app_role() = 'admin'
);

create policy "account managers see assigned clients"
on public.clients
for select
to authenticated
using (
  tenant_id = public.current_tenant_id()
  and (
    public.current_app_role() = 'admin'
    or exists (
      select 1
      from public.client_ownership ownership
      join public.tenant_users tu on tu.id = ownership.user_id
      where ownership.client_id = clients.id
        and ownership.tenant_id = clients.tenant_id
        and ownership.active = true
        and tu.auth_user_id = auth.uid()
    )
  )
);

create policy "admins manage clients"
on public.clients
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

create policy "tenant users read ownership"
on public.client_ownership
for select
to authenticated
using (tenant_id = public.current_tenant_id());

create policy "admins manage ownership"
on public.client_ownership
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

create policy "tenant users read monthly touches"
on public.monthly_touches
for select
to authenticated
using (
  tenant_id = public.current_tenant_id()
  and (
    public.current_app_role() = 'admin'
    or exists (
      select 1
      from public.client_ownership ownership
      join public.tenant_users tu on tu.id = ownership.user_id
      where ownership.client_id = monthly_touches.client_id
        and ownership.tenant_id = monthly_touches.tenant_id
        and ownership.active = true
        and tu.auth_user_id = auth.uid()
    )
  )
);

create policy "admins manage monthly touches"
on public.monthly_touches
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

create policy "tenant users read prompts"
on public.prompt_templates
for select
to authenticated
using (
  tenant_id = public.current_tenant_id()
  or tenant_id is null
);

create policy "admins manage prompts"
on public.prompt_templates
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

create policy "tenant users read prompt versions"
on public.prompt_versions
for select
to authenticated
using (
  exists (
    select 1
    from public.prompt_templates pt
    where pt.id = prompt_versions.prompt_template_id
      and (pt.tenant_id = public.current_tenant_id() or pt.tenant_id is null)
  )
);

create policy "admins manage prompt versions"
on public.prompt_versions
for all
to authenticated
using (
  exists (
    select 1
    from public.prompt_templates pt
    where pt.id = prompt_versions.prompt_template_id
      and pt.tenant_id = public.current_tenant_id()
      and public.current_app_role() = 'admin'
  )
)
with check (
  exists (
    select 1
    from public.prompt_templates pt
    where pt.id = prompt_versions.prompt_template_id
      and pt.tenant_id = public.current_tenant_id()
      and public.current_app_role() = 'admin'
  )
);

create policy "tenant users read audit logs"
on public.audit_logs
for select
to authenticated
using (
  tenant_id = public.current_tenant_id()
  and public.current_app_role() = 'admin'
);

insert into public.tenants (id, name, slug)
values ('11111111-1111-1111-1111-111111111111', 'Northstar Growth', 'northstar-growth')
on conflict (id) do nothing;
