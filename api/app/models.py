from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr


def to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


UserRole = Literal["admin", "account_manager"]
HealthTrend = Literal["up", "down", "stable"]
RiskLevel = Literal["Low", "Medium", "High"]
TouchStage = Literal[
    "Pre-Meeting Intelligence",
    "Meeting Scheduled",
    "Meeting Intelligence",
    "Task Approval",
    "Recap Approval",
    "QA Audit",
]
PromptStatus = Literal["Active", "Draft", "Archived"]
ProviderName = Literal["Claude", "Gemini", "Mixed"]
ActivityKind = Literal["brief", "sync", "risk", "qa", "recap"]
OwnershipExceptionStatus = Literal["open", "resolved"]
IntelligenceSyncStatus = Literal["connected", "warning", "not_found"]
IntegrationHealthStatus = Literal["connected", "warning", "not_configured"]
SyncCursorState = Literal["idle", "running", "completed", "error"]
WorkflowStepStatus = Literal["complete", "current", "upcoming"]
ChecklistItemStatus = Literal["done", "pending"]
ArtifactStatus = Literal["ready", "in_progress", "pending_approval"]
PromptWorkflowStatus = Literal["active", "fallback", "missing"]


class UserProfile(CamelModel):
    id: str
    full_name: str
    role: UserRole
    email: EmailStr


class MetricCard(CamelModel):
    id: str
    label: str
    value: str
    detail: str
    trend: HealthTrend


class ClientRecord(CamelModel):
    id: str
    name: str
    owner: str
    health_score: int
    risk_level: RiskLevel
    next_touch_at: str
    top_opportunity: str


class MonthlyTouchRecord(CamelModel):
    id: str
    client_name: str
    client_id: str | None = None
    scheduled_at: str
    stage: TouchStage
    owner: str


class MonthlyTouchWorkflowStep(CamelModel):
    id: str
    label: str
    status: WorkflowStepStatus
    detail: str


class MonthlyTouchChecklistItem(CamelModel):
    id: str
    label: str
    status: ChecklistItemStatus


class MonthlyTouchArtifact(CamelModel):
    id: str
    label: str
    status: ArtifactStatus
    detail: str


class MonthlyTouchDetail(CamelModel):
    touch: MonthlyTouchRecord
    account_health_score: int
    risk_level: RiskLevel
    executive_summary: str
    top_wins: list[str]
    key_issues: list[str]
    strategic_recommendations: list[str]
    suggested_questions: list[str]
    workflow_steps: list[MonthlyTouchWorkflowStep]
    meeting_checklist: list[MonthlyTouchChecklistItem]
    generated_artifacts: list[MonthlyTouchArtifact]
    prompt_stack: list["PromptWorkflowAssignment"]
    next_action: str


class PromptTemplateRecord(CamelModel):
    id: str
    name: str
    category: str
    version: str
    status: PromptStatus
    provider: ProviderName


class PromptVersionRecord(CamelModel):
    id: str
    version_number: int
    system_prompt: str
    user_prompt: str
    is_active: bool
    created_at: str


class PromptTemplateDetail(CamelModel):
    template: PromptTemplateRecord
    active_version_id: str | None = None
    versions: list[PromptVersionRecord]


class PromptVersionCreateRequest(CamelModel):
    system_prompt: str
    user_prompt: str


class PromptActivationRequest(CamelModel):
    version_id: str


class PromptWorkflowAssignment(CamelModel):
    purpose: str
    template_id: str | None = None
    template_name: str
    version: str
    provider: ProviderName
    status: PromptWorkflowStatus
    detail: str


class ActivityRecord(CamelModel):
    id: str
    title: str
    description: str
    at: str
    kind: ActivityKind


class DashboardOverview(CamelModel):
    tenant_name: str
    current_user: UserProfile
    metrics: list[MetricCard]
    clients: list[ClientRecord]
    monthly_touches: list[MonthlyTouchRecord]
    prompt_templates: list[PromptTemplateRecord]
    activity: list[ActivityRecord]


class ClientWorkspace(CamelModel):
    client: ClientRecord
    monthly_touches: list[MonthlyTouchRecord]
    intelligence_summary: str
    priority_actions: list[str]
    visibility_scope: str
    intelligence_snapshot: "ClientIntelligenceSnapshot | None" = None


class ClientIntelligenceSnapshot(CamelModel):
    id: str
    source: str
    synced_at: str
    sync_status: IntelligenceSyncStatus
    clickup_task_id: str | None = None
    clickup_task_name: str | None = None
    clickup_task_url: str | None = None
    account_manager: str | None = None
    task_status: str | None = None
    task_priority: str | None = None
    due_at: str | None = None
    last_activity_at: str | None = None
    summary: str
    signals: list[str]


class IntegrationConnectionStatus(CamelModel):
    provider: str
    source: str
    configured: bool
    health: IntegrationHealthStatus
    connected_at: str | None = None
    last_verified_at: str | None = None
    last_error: str | None = None


class SyncCursorStatus(CamelModel):
    key: str
    provider: str
    source: str
    status: SyncCursorState
    last_synced_at: str | None = None
    last_cursor: str | None = None
    records_seen: int = 0
    records_processed: int = 0
    last_error: str | None = None


class ClickUpClientImportResult(CamelModel):
    status: Literal["completed"]
    tasks_seen: int
    clients_upserted: int


class TenantContext(CamelModel):
    tenant_id: str
    tenant_name: str
    tenant_user_id: str | None = None
    current_user: UserProfile
    auth_token: str | None = None


class OwnershipExceptionRecord(CamelModel):
    id: str
    client_name: str
    external_account_manager: str
    suggested_user_name: str | None = None
    reason: str
    status: OwnershipExceptionStatus
    last_seen_at: str


class OwnershipSyncSummary(CamelModel):
    provider: str
    source: str
    cadence_minutes: int
    last_run_at: str
    matched_clients: int
    unmatched_clients: int
    exception_count: int


class OwnershipSyncRunResult(CamelModel):
    status: Literal["completed"]
    summary: OwnershipSyncSummary
    exceptions: list[OwnershipExceptionRecord]


class ClickUpIntegrationStatus(CamelModel):
    configured: bool
    base_url: str
    team_id: str | None = None
    list_id: str | None = None
    connection: IntegrationConnectionStatus | None = None
    ownership_cursor: SyncCursorStatus | None = None
    intelligence_cursor: SyncCursorStatus | None = None


class RuntimeCheck(CamelModel):
    key: str
    label: str
    status: Literal["ok", "warning", "error"]
    detail: str


class RuntimeStatus(CamelModel):
    environment: str
    repository_mode: str
    trust_demo_headers: bool
    supabase_configured: bool
    supabase_rls_ready: bool
    recommended_next_step: str
    checks: list[RuntimeCheck]
