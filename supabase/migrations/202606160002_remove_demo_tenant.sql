delete from public.client_intelligence_snapshots
where tenant_id = '11111111-1111-1111-1111-111111111111';

delete from public.ownership_sync_exceptions
where tenant_id = '11111111-1111-1111-1111-111111111111';

delete from public.ownership_sync_runs
where tenant_id = '11111111-1111-1111-1111-111111111111';

delete from public.monthly_touches
where tenant_id = '11111111-1111-1111-1111-111111111111';

delete from public.client_ownership
where tenant_id = '11111111-1111-1111-1111-111111111111';

delete from public.prompt_versions
where prompt_template_id in (
  select id
  from public.prompt_templates
  where tenant_id = '11111111-1111-1111-1111-111111111111'
);

delete from public.prompt_templates
where tenant_id = '11111111-1111-1111-1111-111111111111';

delete from public.audit_logs
where tenant_id = '11111111-1111-1111-1111-111111111111';

delete from public.clients
where tenant_id = '11111111-1111-1111-1111-111111111111';

delete from public.tenant_users
where tenant_id = '11111111-1111-1111-1111-111111111111';

delete from public.tenants
where id = '11111111-1111-1111-1111-111111111111'
   or slug = 'northstar-growth';
