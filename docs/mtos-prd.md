# MTOS Product Requirements Document

## 1. Product Summary

**Product name:** Monthly Touch Operating System (MTOS)

MTOS is an AI-powered Account Management Operating System for agencies. It is purpose-built to operationalize recurring Monthly Touch meetings and the workflows surrounding them: pre-meeting intelligence, meeting analysis, follow-up task generation, client recap automation, quality assurance, coaching, retention improvement, and client growth opportunity detection.

MTOS is not:

- A CRM
- A generic project management platform
- A generic client portal

MTOS exists to help Account Managers run better client relationships at scale while preserving human approval over strategic decisions and outbound actions.

## 2. Mission

Build a production-ready, enterprise-grade SaaS platform that enables agencies to manage hundreds or thousands of clients through a structured Monthly Touch operating system driven by unified client intelligence and controlled AI workflows.

## 3. Core Principles

1. The Monthly Touch is the center of the platform.
2. All intelligence flows from a unified Client Intelligence Engine.
3. Account Managers remain the final decision maker.
4. No AI prompts are hardcoded.
5. Historical context compounds over time through a Learning Engine.
6. Ownership and access control are enforced everywhere.
7. The platform must support multi-tenant, production SaaS operations.

## 4. Primary Users

### 4.1 Admin

Responsibilities:

- Configure workspace settings
- Manage users, roles, prompts, integrations, and automation rules
- View all clients across the tenant
- Audit outputs, QA performance, retention trends, and operational health

### 4.2 Account Manager

Responsibilities:

- Review Monthly Touch briefs
- Run Monthly Touch meetings
- Approve tasks, recap emails, and follow-up actions
- Track client health, risks, and opportunities
- Manage only assigned clients

### 4.3 Leadership / Ops

Responsibilities:

- Monitor retention risk
- Review QA performance and coaching recommendations
- Identify revenue leakage, delivery issues, and growth opportunities

## 5. Business Outcomes

MTOS should help agencies:

- Standardize Monthly Touch execution
- Reduce meeting prep time
- Increase follow-through after meetings
- Detect churn risk earlier
- Identify upsell opportunities faster
- Improve client satisfaction and retention
- Improve AM consistency through QA and coaching
- Reduce revenue leakage from missed follow-up and poor lead handling

## 6. Product Scope

### 6.1 In Scope for MVP+

- Multi-tenant SaaS authentication and authorization
- Client ownership sync from ClickUp Client Health Tracker
- Client Intelligence Engine ingestion and normalized storage
- Monthly Touch scheduling visibility and lifecycle orchestration
- AI-generated Monthly Touch Briefs
- Meeting transcript ingestion and meeting intelligence analysis
- Task extraction and ClickUp draft task creation
- Client recap email generation with approval flow
- QA audits and coaching recommendations
- Learning Engine persistence and historical reuse
- Prompt Management Center with versioning and testing
- Roadmaps, reviews, discovery captures, content captures, and operational accountability modules
- Revenue leakage and opportunity detection
- Audit logs, admin controls, and observability

### 6.2 Out of Scope

- Full CRM pipeline replacement
- General-purpose PM functionality outside Monthly Touch operations
- Unapproved autonomous client communication
- Direct AI decision-making without review in critical outbound workflows

## 7. Functional Requirements

### 7.1 Workspace and Tenant Management

- Each agency is a tenant with strict data isolation.
- Each tenant has users, clients, integrations, prompts, jobs, outputs, and audit logs.
- Tenant configuration is environment-driven and admin-managed where appropriate.

### 7.2 Authentication and Roles

- Use Supabase Auth for authentication.
- Support at minimum:
  - `admin`
  - `account_manager`
  - `leadership` optional extension
- Admin sees all clients.
- Account Manager only sees assigned clients.
- RBAC and ownership filters must be enforced on every API endpoint, query, and UI route.

### 7.3 Client Ownership Sync

Source of truth:

- ClickUp Client Health Tracker

Sync cadence:

- Every 15 minutes

Behavior:

- Pull tracker records
- Read Account Manager field
- Match AM to MTOS user
- Upsert ownership mapping
- Record sync results and failures

Failure handling:

- Unmatched AM names enter exception queue
- Admin can resolve mapping manually
- Sync retries with exponential backoff

### 7.4 Client Intelligence Engine

The Client Intelligence Engine is the mandatory upstream layer for all AI workflows. It unifies data from:

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

Requirements:

- Normalize external data into internal canonical models
- Maintain source lineage and sync timestamps
- Support incremental sync
- Support historical snapshots for trend analysis
- Provide unified client context for downstream AI workflows
- Prevent duplicate direct integration reads when normalized context already exists

### 7.5 AI Router

The AI Router is the orchestration layer for all AI operations.

Responsibilities:

- Provider selection
- Model selection
- Prompt selection
- Tool and workflow orchestration
- Cost and latency controls
- Response logging and traceability

Gemini responsibilities:

- Classification
- Categorization
- Summaries
- Ticket drafting
- Lead analysis
- Revenue leakage detection

Claude responsibilities:

- Monthly Touch briefs
- Strategic analysis
- Client health scoring
- Meeting analysis
- QA audits
- Coaching
- Retention analysis
- Client recap emails

Requirements:

- Configurable fallback model strategy
- Runtime prompt resolution by category and version
- Per-workflow observability
- Token, latency, and failure tracking

### 7.6 Prompt Management Center

No prompts may be hardcoded in business logic.

Required prompt categories:

- Monthly Touch Brief Structure
- Monthly Touch Meeting Framework
- Monthly Touch Analysis Framework
- Revenue Leakage Analysis
- Lead Quality Analysis
- Call Quality Analysis
- Follow-Up Analysis
- Transcript Analysis
- Ticket Extraction Rules
- Client Recap Email
- QA Audit Rubric
- Coaching Framework
- Retention Analysis

Prompt features:

- Create
- Edit
- Duplicate
- Archive
- Version history
- Prompt testing
- Rollback to previous versions
- Enable/disable by tenant or global scope

### 7.7 Learning Engine

The Learning Engine stores longitudinal account knowledge and improves future outputs.

Must store:

- Meeting history
- Client preferences
- Sentiment trends
- Wins
- Issues
- Risks
- Recommendations
- Previous briefs
- Previous QA reports

Requirements:

- Future Monthly Touch Briefs must use historical context
- Time-series signals must support trend analysis
- Stored learnings must remain tenant-scoped and client-scoped

### 7.8 Monthly Touch Lifecycle

#### Stage 1: Pre-Meeting Intelligence

Trigger:

- 24 hours before Monthly Touch

Requirements:

- Generate Monthly Touch Brief automatically
- Use rolling analysis window
- Support `30d`, `60d`, `90d`, and `custom`
- Tenant admin can configure default lookback

Brief contents:

- Executive Summary
- Client Health Score
- Top 3 Wins
- Wins Library
- Top 2 Issues
- Issues Library
- Revenue Leakage Report
- Lead Follow-Up Report
- Call Quality Report
- Google Ads Analysis
- GBP Analysis
- Search Console Analysis
- Analytics Analysis
- Rank Tracker Analysis
- Ahrefs Analysis
- Trend Comparison
- Retention Risks
- Upsell Opportunities
- Talking Points
- Discussion Questions
- Suggested Agenda
- Next Best Actions

#### Stage 2: Meeting

Requirements:

- Associate the scheduled Monthly Touch with Google Meet metadata where available
- Store recording reference
- Ingest transcript
- Ingest or generate notes

#### Stage 3: Meeting Intelligence

Analyze:

- Decisions
- Requests
- Risks
- Concerns
- Opportunities
- Commitments
- Action Items

Output:

- Meeting Intelligence Report

#### Stage 4: Ticket Generation

Requirements:

- Extract tasks from meeting outputs
- Categorize by:
  - SEO
  - PPC
  - Website
  - GBP
  - Content
  - Design
  - Automation
- Generate ClickUp draft tasks
- Require Account Manager approval before creation

#### Stage 5: Client Recap

Requirements:

- Generate recap email draft
- Require Account Manager approval
- Support automatic send only after approval
- Persist sent version and delivery status

#### Stage 6: QA Audit

Evaluate:

- Rapport
- Structure
- KPI Discussion
- Opportunity Discovery
- Client Engagement
- Follow-Up Planning
- Action Planning

Generate:

- QA Score
- Strengths
- Weaknesses
- Coaching Recommendations

#### Stage 7: Learning

Requirements:

- Persist artifacts from all prior stages
- Update longitudinal client context
- Feed future brief generation and retention analysis

## 8. Additional Product Modules

The complete platform should also include:

- Roadmap management
- Reviews management
- Discovery capture
- Content capture workflows
- QA scorecards
- Revenue leakage monitoring
- Operational accountability dashboards
- AI visibility and reporting

## 9. Non-Functional Requirements

### 9.1 Performance

- Dashboard and client views should feel responsive for agencies with thousands of clients.
- Background jobs must support batched and incremental processing.
- AI orchestration must support async execution and retries.

### 9.2 Security

- Enforce tenant isolation with PostgreSQL Row Level Security.
- Encrypt secrets and sensitive tokens.
- Maintain audit logs for admin actions, AI output approvals, and integration changes.
- Support least privilege scopes for external integrations.

### 9.3 Reliability

- Idempotent ingestion and job execution
- Retry policies with dead-letter handling
- Health checks for API, workers, database connectivity, and integrations

### 9.4 Observability

- Structured logs
- Request tracing
- Background job monitoring
- AI workflow telemetry
- Sync and integration health reporting

### 9.5 Compliance Readiness

- Tenant data separation
- Role-based permissions
- Audit trails
- Data retention and deletion workflows

## 10. Success Metrics

- Monthly Touch brief generation success rate
- Average brief preparation time saved
- Approval-to-task creation conversion rate
- Client recap send rate
- QA completion coverage
- Retention risk detection accuracy proxy metrics
- Upsell opportunity detection rate
- Revenue leakage findings per client cohort
- AM adoption and weekly active usage

## 11. Acceptance Criteria

The specification is complete when engineering can implement MTOS with:

- A multi-tenant architecture
- Enforced ownership-based visibility
- Unified intelligence ingestion
- Configurable AI orchestration
- Prompt versioning and testing
- Full Monthly Touch lifecycle automation with human approvals
- Historical learning persistence
- Operational modules and auditability suitable for production SaaS use
