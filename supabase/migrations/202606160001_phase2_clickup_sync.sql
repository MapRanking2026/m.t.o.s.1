-- Phase 2: guardrails for ownership sync

create unique index if not exists idx_client_ownership_one_active
on public.client_ownership (tenant_id, client_id)
where active;

create unique index if not exists idx_ownership_sync_exceptions_one_open
on public.ownership_sync_exceptions (tenant_id, client_name, external_account_manager, reason)
where status = 'open';

