# MTOS Build Plan

## 1. Delivery Strategy

MTOS should be built in vertical slices, not isolated technical layers. Each phase should ship an end-to-end capability that is deployable, testable, and useful in staging.

Guiding rules:

1. Establish tenant safety first.
2. Build the unified intelligence layer before advanced AI features.
3. Introduce human approval gates before automation that affects clients or delivery systems.
4. Ship observability alongside workflows, not afterward.

## 2. Phase Plan

### Phase 0: Foundation

Deliverables:

- Monorepo setup
- Frontend scaffold with routing, state, design system, auth shell
- FastAPI scaffold with domain modules
- Supabase project, base schema, and RLS strategy
- Docker local development stack
- GitHub Actions pipeline
- Environment configuration framework
- Audit logging foundation

Exit criteria:

- Users can authenticate
- Tenant and role context resolves correctly
- Protected API routes work
- Database migrations run cleanly
- CI passes

### Phase 1: Core SaaS and Access Control

Deliverables:

- Tenant, user, role, and membership management
- Client records
- Ownership model
- Ownership-based UI filtering
- Admin and AM permissions
- Ownership sync exception handling skeleton

Exit criteria:

- Admin can see all clients
- Account Manager can only see assigned clients
- RLS blocks unauthorized reads and writes
- Client list and detail pages load with correct access scope

### Phase 2: Integration Foundation and Client Intelligence Engine

Deliverables:

- Integration connection framework
- Connector abstraction layer
- ClickUp connector first
- Normalized data schemas
- Sync jobs and cursors
- Client Intelligence Engine service
- Timeline and metrics snapshot views

Priority providers in this phase:

- ClickUp
- Google Analytics
- Google Search Console
- Google Ads

Exit criteria:

- At least one client can be fully synced from ClickUp ownership source
- Intelligence data is normalized and queryable
- Downstream workflows can consume unified client context

### Phase 3: Monthly Touch Scheduling and Brief Generation

Deliverables:

- Monthly Touch scheduling model
- Lookback window configuration
- Pre-meeting job triggers
- AI Router v1
- Prompt Management Center v1
- Monthly Touch Brief generation
- Brief review UI

Exit criteria:

- Brief auto-generates 24 hours before meeting in staging
- Prompt versions are selected dynamically
- Brief content persists and is reviewable by AM

### Phase 4: Meeting Artifacts and Intelligence

Deliverables:

- Google Meet and transcript ingestion pipeline
- Recording and transcript artifact storage references
- Meeting notes support
- Meeting Intelligence analysis workflow
- Client timeline updates from meeting outputs

Exit criteria:

- Transcript can be attached to Monthly Touch
- Meeting Intelligence Report is generated from transcript plus context
- Decisions, requests, risks, and action items are extracted reliably

### Phase 5: Task Drafting and Recap Workflow

Deliverables:

- Task extraction rules via prompts
- Draft task objects
- ClickUp task creation integration
- Approval and rejection UI
- Recap email generation
- Approved send flow

Exit criteria:

- AM can approve draft tasks before ClickUp creation
- AM can approve recap before send
- All outbound actions are logged

### Phase 6: QA, Coaching, and Learning Engine

Deliverables:

- QA rubric prompt set
- QA scoring service
- Coaching recommendation generation
- Learning memory persistence
- Historical retrieval in future briefs

Exit criteria:

- QA score and recommendations generate per meeting
- Brief generation uses prior meeting intelligence and learned client context

### Phase 7: Advanced Intelligence and Operations Modules

Deliverables:

- Revenue leakage analysis
- Retention analysis
- Upsell and opportunity surfacing
- Reviews management
- Roadmap management
- Discovery capture
- Content captures
- Operational accountability dashboards

Exit criteria:

- Leadership can review retention risk and revenue leakage dashboards
- AMs can manage supporting account workflows inside MTOS

### Phase 8: Production Hardening

Deliverables:

- Load testing
- Security review
- Failure injection and retry validation
- Alerting and dashboards
- Backup and recovery procedures
- Runbooks and support documentation

Exit criteria:

- Staging signoff complete
- Core workflows monitored with alerts
- Deployment and rollback documented

## 3. Recommended Build Order by Team

### Product

- Finalize workflow states
- Define approval policies
- Lock acceptance criteria for each phase

### Architecture

- Finalize schema
- Define canonical normalized models
- Define AI workflow contracts
- Define RLS policies

### Frontend

- App shell
- Client workspace
- Monthly Touch workflow screens
- Prompt center
- Admin tools

### Backend

- Identity and access domain
- Client and ownership domain
- Integration framework
- AI Router
- Workflow orchestration

### QA

- Access control test plan
- Integration sync validation plan
- AI workflow review harness
- Production readiness checklist

## 4. Testing Strategy

### 4.1 Backend

- Unit tests for domain services
- Integration tests for API endpoints
- RLS and authorization tests
- Connector normalization tests
- Job idempotency and retry tests

### 4.2 Frontend

- Component tests for critical workflow screens
- End-to-end tests for auth, client access, brief approval, task approval, and recap approval

### 4.3 AI Workflows

- Prompt regression fixtures
- Golden-output evaluation sets
- Cost and latency monitoring thresholds
- Human review sampling for output quality

## 5. Operational Readiness Checklist

- Secrets managed outside source code
- Separate staging and production environments
- Audit logs retained
- Background jobs observable
- Dead letters reviewable
- Integration health visible in admin
- AI runs traceable to model and prompt version
- Client ownership enforcement verified

## 6. MVP Definition

An acceptable first production launch of MTOS includes:

- Multi-tenant auth and RBAC
- Client ownership sync from ClickUp
- Unified intelligence context for core sources
- Monthly Touch scheduling and brief generation
- Meeting transcript ingestion
- Meeting intelligence reporting
- Draft task creation with approval
- Recap email generation with approval
- QA scoring and coaching
- Prompt Management Center
- Learning Engine basics

## 7. Post-MVP Expansion

- Broader connector coverage
- Deeper retention analytics
- Roadmap collaboration enhancements
- Review response workflows
- More advanced AI benchmarking and routing policies
- Multi-role leadership scorecards

## 8. Immediate Next Engineering Tasks

1. Create the monorepo scaffold and local Docker environment.
2. Implement Supabase schema for tenants, users, clients, ownership, and audit logs.
3. Build FastAPI auth context and authorization middleware.
4. Build React app shell with protected routes and tenant-aware navigation.
5. Implement ClickUp ownership sync and exception queue.
6. Add Client Intelligence Engine schemas and first sync pipeline.
7. Build Monthly Touch data model and brief generation workflow.
