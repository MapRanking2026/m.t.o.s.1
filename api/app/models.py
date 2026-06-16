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
    scheduled_at: str
    stage: TouchStage
    owner: str


class PromptTemplateRecord(CamelModel):
    id: str
    name: str
    category: str
    version: str
    status: PromptStatus
    provider: ProviderName


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
