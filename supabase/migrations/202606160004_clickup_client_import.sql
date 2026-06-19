create unique index if not exists idx_clients_tenant_external_ref_unique
  on public.clients (tenant_id, external_ref)
  where external_ref is not null;
