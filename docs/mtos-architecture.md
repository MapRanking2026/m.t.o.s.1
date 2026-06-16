# MTOS System Architecture

## 1. Architecture Goals

MTOS must operate as a production-grade, multi-tenant SaaS platform that supports:

- Hundreds to thousands of clients per agency
- Strict ownership-based visibility
- High-volume ingestion from external systems
- AI-driven workflows with human approval gates
- Historical learning and trend analysis
- Safe deployment, observability, and auditability

## 2. Recommended Monorepo Layout

```text
mtos/
  apps/
    web/                    # React + Vite frontend
    api/                    # FastAPI application
    worker/                 # Async job runner
  packages/
    ui/                     # Shared shadcn/ui wrappers and design system
    client-sdk/             # Typed API client for frontend
    shared-types/           # Cross-app contracts where useful
    prompts/                # Prompt schemas and local fixtures, not prompt content
  infra/
    docker/
    github-actions/
    cloudflare/
    db/
  docs/
```

## 3. Technology Decisions

### 3.1 Frontend

- React
- Vite
- TypeScript
- Tailwind CSS
- React Router
- TanStack Query
- Zustand
- shadcn/ui

Responsibilities:

- Authenticated SaaS application shell
- Client, meeting, and intelligence dashboards
- Approval workflows
- Prompt management UI
- Admin configuration and audit views

### 3.2 Backend

- FastAPI
- Python
- Pydantic
- Async architecture

Responsibilities:

- REST API for frontend
- Webhook receivers
- AI workflow orchestration
- Integration connectors
- Background job coordination
- Authorization enforcement

### 3.3 Database

- Supabase PostgreSQL
- Supabase Auth
- Row Level Security

Responsibilities:

- Tenant-scoped operational data
- Auth and session integration
- AI outputs and prompt versions
- Historical intelligence storage
- Audit logs and sync jobs

### 3.4 Infrastructure

- Docker
- Cloudflare
- GitHub Actions
- Environment-driven configuration

## 4. High-Level Components

### 4.1 Web App

Core areas:

- Auth and onboarding
- Global navigation
- Client workspace
- Monthly Touch pipeline
- Intelligence views
- Prompt center
- QA and coaching dashboards
- Admin and settings

### 4.2 API Service

Domain modules:

- Identity and access
- Tenants and users
- Clients and ownership
- Integrations and sync
- Intelligence aggregation
- Meetings and transcripts
- AI router
- Prompt management
- Task generation
- Email recap
- QA and coaching
- Learning engine
- Reporting and analytics
- Audit and compliance

### 4.3 Worker Service

Async responsibilities:

- Scheduled sync jobs
- Pre-meeting brief generation
- Transcript processing
- Meeting intelligence analysis
- Task draft generation
- Recap email rendering and delivery
- QA scoring
- Learning updates
- Retry and dead-letter handling

## 5. Multi-Tenancy Model

### 5.1 Tenant Strategy

- Single logical application
- Shared database with tenant-scoped rows
- `tenant_id` on all tenant-owned records
- Row Level Security on all protected tables

### 5.2 Authorization Strategy

Authorization is a combination of:

- User role
- Tenant membership
- Client ownership

Rules:

- `admin`: full tenant visibility
- `account_manager`: only clients explicitly assigned through ownership sync or manual override

Enforcement points:

- Database RLS
- API service guards
- Query builders
- Frontend route guards and filtering

Database enforcement is the source of truth.

## 6. Domain Model

### 6.1 Core Entities

- `tenants`
- `users`
- `tenant_users`
- `clients`
- `client_ownership`
- `monthly_touches`
- `meeting_artifacts`
- `meeting_transcripts`
- `meeting_notes`
- `meeting_intelligence_reports`
- `briefs`
- `brief_sections`
- `tasks_draft`
- `recap_emails`
- `qa_audits`
- `coaching_reports`
- `learning_memories`
- `prompt_templates`
- `prompt_versions`
- `ai_runs`
- `integration_connections`
- `integration_sync_jobs`
- `integration_sync_state`
- `normalized_signals`
- `normalized_metrics_snapshots`
- `roadmaps`
- `reviews`
- `discovery_captures`
- `content_captures`
- `revenue_leakage_findings`
- `audit_logs`

### 6.2 Key Relationships

- Tenant has many users and clients
- Client has one active owner and ownership history
- Client has many Monthly Touch records
- Monthly Touch has one brief, many artifacts, one intelligence report, many draft tasks, one recap draft, and one QA audit
- AI runs reference prompt version, model, provider, input context, and output artifact
- Learning memories link to client and specific source artifact types

## 7. Suggested Database Design

### 7.1 Identity Tables

- `tenants(id, name, slug, status, created_at)`
- `profiles(id, auth_user_id, full_name, email, created_at)`
- `tenant_users(id, tenant_id, profile_id, role, status, created_at)`

### 7.2 Client Tables

- `clients(id, tenant_id, external_ref, name, status, segment, timezone, created_at)`
- `client_ownership(id, tenant_id, client_id, user_id, source, synced_at, active)`
- `client_health_snapshots(id, tenant_id, client_id, score, status, factors, created_at)`

### 7.3 Meeting Tables

- `monthly_touches(id, tenant_id, client_id, scheduled_at, status, lookback_window_days, meet_url, created_at)`
- `meeting_recordings(id, tenant_id, monthly_touch_id, storage_url, source, created_at)`
- `meeting_transcripts(id, tenant_id, monthly_touch_id, transcript_text, provider, created_at)`
- `meeting_notes(id, tenant_id, monthly_touch_id, notes_markdown, source, created_at)`

### 7.4 AI Output Tables

- `briefs(id, tenant_id, client_id, monthly_touch_id, status, generated_at, approved_by)`
- `meeting_intelligence_reports(id, tenant_id, monthly_touch_id, status, payload_json, generated_at)`
- `task_drafts(id, tenant_id, monthly_touch_id, category, title, description, status, approved_by, created_at)`
- `recap_emails(id, tenant_id, monthly_touch_id, subject, body_html, status, approved_by, sent_at)`
- `qa_audits(id, tenant_id, monthly_touch_id, score, rubric_version_id, status, generated_at)`
- `coaching_reports(id, tenant_id, monthly_touch_id, payload_json, generated_at)`

### 7.5 Prompt Tables

- `prompt_templates(id, tenant_id nullable, category, name, status, created_by, created_at)`
- `prompt_versions(id, prompt_template_id, version_number, system_prompt, user_prompt, config_json, is_active, created_at)`
- `prompt_test_runs(id, prompt_version_id, input_json, output_json, evaluation_notes, created_at)`

### 7.6 AI Telemetry Tables

- `ai_runs(id, tenant_id, client_id nullable, monthly_touch_id nullable, workflow_type, provider, model, prompt_version_id, status, token_input, token_output, latency_ms, cost_usd, error_json, created_at)`

### 7.7 Integration Tables

- `integration_connections(id, tenant_id, provider, status, credentials_ref, scopes_json, created_at)`
- `integration_sync_jobs(id, tenant_id, provider, sync_type, status, started_at, finished_at, error_json)`
- `integration_sync_state(id, tenant_id, provider, external_cursor, last_synced_at, metadata_json)`
- `normalized_signals(id, tenant_id, client_id, source, signal_type, payload_json, observed_at)`
- `normalized_metrics_snapshots(id, tenant_id, client_id, source, metric_date, metrics_json)`

### 7.8 Learning Tables

- `learning_memories(id, tenant_id, client_id, memory_type, source_type, source_id, summary, payload_json, observed_at, created_at)`
- `sentiment_trends(id, tenant_id, client_id, period_start, period_end, score, rationale_json)`

### 7.9 Governance Tables

- `audit_logs(id, tenant_id, actor_user_id, entity_type, entity_id, action, metadata_json, created_at)`
- `job_dead_letters(id, tenant_id nullable, job_type, payload_json, error_json, created_at)`

## 8. API Design

### 8.1 API Principles

- Versioned REST API under `/api/v1`
- Async endpoints for long-running workflows
- Frontend polls job status or subscribes to updates later
- Pydantic request and response contracts
- All endpoints require tenant and role context

### 8.2 Endpoint Groups

Authentication and session:

- `GET /api/v1/me`
- `GET /api/v1/session`

Users and access:

- `GET /api/v1/users`
- `POST /api/v1/users/invite`
- `PATCH /api/v1/users/{id}/role`

Clients:

- `GET /api/v1/clients`
- `GET /api/v1/clients/{id}`
- `GET /api/v1/clients/{id}/timeline`
- `GET /api/v1/clients/{id}/health`
- `GET /api/v1/clients/{id}/intelligence`

Ownership:

- `POST /api/v1/ownership/sync`
- `GET /api/v1/ownership/exceptions`
- `POST /api/v1/ownership/exceptions/{id}/resolve`

Monthly Touches:

- `GET /api/v1/monthly-touches`
- `POST /api/v1/monthly-touches`
- `GET /api/v1/monthly-touches/{id}`
- `POST /api/v1/monthly-touches/{id}/generate-brief`
- `POST /api/v1/monthly-touches/{id}/analyze-meeting`
- `POST /api/v1/monthly-touches/{id}/generate-tasks`
- `POST /api/v1/monthly-touches/{id}/generate-recap`
- `POST /api/v1/monthly-touches/{id}/run-qa`

Approvals:

- `POST /api/v1/task-drafts/{id}/approve`
- `POST /api/v1/task-drafts/{id}/reject`
- `POST /api/v1/recap-emails/{id}/approve`
- `POST /api/v1/recap-emails/{id}/send`

Prompts:

- `GET /api/v1/prompts`
- `POST /api/v1/prompts`
- `GET /api/v1/prompts/{id}/versions`
- `POST /api/v1/prompts/{id}/versions`
- `POST /api/v1/prompts/{id}/duplicate`
- `POST /api/v1/prompts/test`

Integrations:

- `GET /api/v1/integrations`
- `POST /api/v1/integrations/{provider}/connect`
- `POST /api/v1/integrations/{provider}/sync`
- `GET /api/v1/integrations/{provider}/health`

Reporting:

- `GET /api/v1/reports/retention`
- `GET /api/v1/reports/revenue-leakage`
- `GET /api/v1/reports/qa`
- `GET /api/v1/reports/adoption`

## 9. AI Architecture

### 9.1 Layer 1: Client Intelligence Engine

Pipeline:

1. Connector pulls source data
2. Raw payload is stored or logged for traceability
3. Normalizer maps data to canonical schemas
4. Signals and metrics snapshots are persisted
5. Unified client context is assembled for downstream workflows

Canonical context should include:

- Account metadata
- Performance metrics
- Trend deltas
- Open issues
- Delivery and task signals
- Communication history
- Review and reputation signals
- Historical Monthly Touch artifacts

### 9.2 Layer 2: AI Router

Router inputs:

- Workflow type
- Tenant configuration
- Prompt category
- Input context size
- SLA or latency target
- Cost budget

Router outputs:

- Selected provider
- Selected model
- Selected prompt version
- Tool chain
- Run metadata and telemetry

### 9.3 Layer 3: Prompt Management Center

Prompt rendering rules:

- Resolve active prompt by category and tenant scope
- Compose variables with validated structured inputs
- Store exact prompt version used for every AI run

### 9.4 Layer 4: Learning Engine

Learning retrieval should support:

- Last 3 Monthly Touch summaries
- Preference memory
- Trend deltas over configurable windows
- Unresolved issues carried forward
- Historical QA and coaching notes

## 10. Integration Architecture

### 10.1 Connector Pattern

Each provider connector should implement:

- `authorize()`
- `refresh_credentials()`
- `sync_accounts()`
- `sync_client_data(client_ref, cursor)`
- `normalize(payload)`
- `health_check()`

### 10.2 Required Providers

- ClickUp
- GoHighLevel
- Google Ads
- Google Business Profile
- Google Search Console
- Google Analytics
- Gmail
- Google Drive
- Google Meet
- Rank Tracker
- Ahrefs

### 10.3 Sync Strategy

- Scheduled sync for stable reporting sources
- Event or webhook-driven ingestion where available
- Backfill jobs for historical data
- Cursor-based incremental sync
- Idempotent upserts

## 11. Background Job Design

Recommended job types:

- `ownership_sync_job`
- `integration_sync_job`
- `brief_generation_job`
- `transcript_ingestion_job`
- `meeting_analysis_job`
- `task_drafting_job`
- `recap_generation_job`
- `recap_send_job`
- `qa_audit_job`
- `learning_update_job`
- `retention_analysis_job`

Job requirements:

- Idempotent execution key
- Retry policy
- Dead-letter queue
- Structured status model
- Operator visibility in admin UI

## 12. Frontend Information Architecture

Primary navigation:

- Dashboard
- Clients
- Monthly Touches
- Intelligence
- Tasks
- QA and Coaching
- Reviews
- Roadmaps
- Discovery
- Content Captures
- Reports
- Prompt Center
- Integrations
- Admin

Key screens:

- Login and invite acceptance
- Tenant overview dashboard
- Client list with ownership filters
- Client 360 workspace
- Monthly Touch detail page
- Brief review screen
- Meeting intelligence screen
- Draft task approval screen
- Recap approval screen
- QA audit screen
- Prompt template library
- Prompt version editor and tester
- Integration status center
- Ownership exception queue
- Retention and revenue leakage dashboards

## 13. Security Design

- Supabase Auth for user identity
- Service role usage restricted to backend only
- Encrypted secret storage
- RLS for all tenant tables
- API authorization middleware
- Per-provider token scope minimization
- Audit logs for sensitive actions
- Signed URLs or controlled access for recordings and transcript artifacts

## 14. Deployment Design

### 14.1 Runtime Services

- `web`
- `api`
- `worker`
- `postgres` managed by Supabase
- optional `redis` or queue layer if introduced

### 14.2 Environments

- `local`
- `staging`
- `production`

### 14.3 CI/CD

GitHub Actions should run:

- Lint
- Type check
- Unit tests
- Build frontend
- Build backend
- Run migrations validation
- Build Docker images
- Deploy to staging or production by branch policy

## 15. Observability

- Centralized structured logging
- API request tracing
- Worker job tracing
- AI run telemetry
- Sync success/failure dashboards
- Alerting for failed syncs, job dead letters, and elevated AI error rates

## 16. Recommended Implementation Standards

- Use domain-oriented backend modules
- Keep prompt text in database, not source code
- Keep integration normalization schemas explicit and versioned
- Use typed frontend API hooks
- Protect every client-scoped query with ownership constraints
- Treat AI outputs as draft artifacts until approved where user-facing or externally impactful
