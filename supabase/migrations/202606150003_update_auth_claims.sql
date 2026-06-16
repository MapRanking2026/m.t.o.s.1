create or replace function public.current_tenant_id()
returns uuid
language sql
stable
as $$
  select coalesce(
    nullif(auth.jwt() ->> 'tenant_id', '')::uuid,
    nullif((auth.jwt() -> 'app_metadata' ->> 'tenant_id'), '')::uuid
  );
$$;

create or replace function public.current_app_role()
returns text
language sql
stable
as $$
  select coalesce(
    nullif(auth.jwt() ->> 'app_role', ''),
    nullif((auth.jwt() -> 'app_metadata' ->> 'app_role'), ''),
    'account_manager'
  );
$$;

