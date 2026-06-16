alter table public.clients
  add column if not exists health_score integer not null default 0,
  add column if not exists risk_level text not null default 'Low',
  add column if not exists next_touch_at text,
  add column if not exists top_opportunity text;

alter table public.prompt_templates
  add column if not exists provider text not null default 'Mixed',
  add column if not exists active_version text not null default 'v1';

