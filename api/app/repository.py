from copy import deepcopy
from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.models import (
    ActivityRecord,
    ClientIntelligenceSnapshot,
    ClientRecord,
    ClientWorkspace,
    DashboardOverview,
    MetricCard,
    MonthlyTouchRecord,
    OwnershipExceptionRecord,
    OwnershipSyncRunResult,
    OwnershipSyncSummary,
    PromptTemplateRecord,
    TenantContext,
    UserProfile,
)


class InMemoryMTOSRepository:
    def __init__(self) -> None:
        self.tenant_id = "tenant_1"
        self.tenant_name = "MTOS Workspace"
        self._users = [
            UserProfile(
                id="user_1",
                full_name="Ariana Cole",
                role="admin",
                email="ariana@northstargrowth.com",
            ),
            UserProfile(
                id="user_2",
                full_name="Mila Grant",
                role="account_manager",
                email="mila@northstargrowth.com",
            ),
            UserProfile(
                id="user_3",
                full_name="Leo Parker",
                role="account_manager",
                email="leo@northstargrowth.com",
            ),
        ]
        self._clients = [
            ClientRecord(
                id="client_1",
                name="BluePeak Dental",
                owner="Ariana Cole",
                health_score=84,
                risk_level="Low",
                next_touch_at="Jun 18 · 11:00 AM",
                top_opportunity="GBP optimization",
            ),
            ClientRecord(
                id="client_2",
                name="Northwind Legal",
                owner="Mila Grant",
                health_score=67,
                risk_level="Medium",
                next_touch_at="Jun 19 · 2:30 PM",
                top_opportunity="Lead qualification automation",
            ),
            ClientRecord(
                id="client_3",
                name="Harbor Ortho",
                owner="Ariana Cole",
                health_score=51,
                risk_level="High",
                next_touch_at="Jun 20 · 9:00 AM",
                top_opportunity="Retention rescue plan",
            ),
            ClientRecord(
                id="client_4",
                name="Verdant Med Spa",
                owner="Leo Parker",
                health_score=76,
                risk_level="Low",
                next_touch_at="Jun 21 · 1:30 PM",
                top_opportunity="Paid social expansion",
            ),
        ]
        self._monthly_touches = [
            MonthlyTouchRecord(
                id="touch_1",
                client_name="BluePeak Dental",
                scheduled_at="Jun 18 · 11:00 AM",
                stage="Pre-Meeting Intelligence",
                owner="Ariana Cole",
            ),
            MonthlyTouchRecord(
                id="touch_2",
                client_name="Northwind Legal",
                scheduled_at="Jun 19 · 2:30 PM",
                stage="Task Approval",
                owner="Mila Grant",
            ),
            MonthlyTouchRecord(
                id="touch_3",
                client_name="Harbor Ortho",
                scheduled_at="Jun 20 · 9:00 AM",
                stage="QA Audit",
                owner="Ariana Cole",
            ),
            MonthlyTouchRecord(
                id="touch_4",
                client_name="Verdant Med Spa",
                scheduled_at="Jun 21 · 1:30 PM",
                stage="Recap Approval",
                owner="Leo Parker",
            ),
        ]
        self._prompt_templates = [
            PromptTemplateRecord(
                id="prompt_1",
                name="Monthly Touch Brief Structure",
                category="Monthly Touch",
                version="v12",
                status="Active",
                provider="Claude",
            ),
            PromptTemplateRecord(
                id="prompt_2",
                name="Ticket Extraction Rules",
                category="Follow-Up",
                version="v6",
                status="Active",
                provider="Gemini",
            ),
            PromptTemplateRecord(
                id="prompt_3",
                name="Retention Analysis",
                category="Retention",
                version="v4",
                status="Draft",
                provider="Mixed",
            ),
        ]
        self._activity = [
            ActivityRecord(
                id="activity_1",
                title="Brief generated for BluePeak Dental",
                description="30 day unified context compiled from Search Console, GBP, Ads, and ClickUp.",
                at="2m ago",
                kind="brief",
            ),
            ActivityRecord(
                id="activity_2",
                title="Ownership sync completed",
                description="ClickUp Client Health Tracker matched 112 of 115 account manager assignments.",
                at="16m ago",
                kind="sync",
            ),
            ActivityRecord(
                id="activity_3",
                title="Revenue leakage flagged",
                description="Northwind Legal has unresolved lead follow-up gaps and ad spend inefficiency.",
                at="24m ago",
                kind="risk",
            ),
            ActivityRecord(
                id="activity_4",
                title="QA score posted",
                description="Harbor Ortho scored 88 with coaching notes on discovery depth and action framing.",
                at="48m ago",
                kind="qa",
            ),
        ]
        self._exceptions = [
            OwnershipExceptionRecord(
                id="exception_1",
                client_name="Harbor Ortho",
                external_account_manager="Ari Cole",
                suggested_user_name="Ariana Cole",
                reason="ClickUp AM label does not exactly match an MTOS user name.",
                status="open",
                last_seen_at="2026-06-15T12:10:00Z",
            ),
            OwnershipExceptionRecord(
                id="exception_2",
                client_name="Blue Valley Dental",
                external_account_manager="Samir Patel",
                suggested_user_name=None,
                reason="No MTOS user matches the ClickUp Account Manager field.",
                status="open",
                last_seen_at="2026-06-15T12:10:00Z",
            ),
        ]
        self._sync_summary = OwnershipSyncSummary(
            provider="ClickUp",
            source="Client Health Tracker",
            cadence_minutes=15,
            last_run_at="2026-06-15T12:10:00Z",
            matched_clients=112,
            unmatched_clients=3,
            exception_count=len(self._exceptions),
        )
        self._intelligence_snapshots = {
            "client_1": ClientIntelligenceSnapshot(
                id="snapshot_1",
                source="ClickUp",
                synced_at="2026-06-16T09:00:00Z",
                sync_status="connected",
                clickup_task_id="task_1",
                clickup_task_name="BluePeak Dental",
                clickup_task_url="https://app.clickup.com/t/task_1",
                account_manager="Ariana Cole",
                task_status="on track",
                task_priority="High",
                due_at="2026-06-18T16:00:00Z",
                last_activity_at="2026-06-16T08:45:00Z",
                summary="Matched ClickUp tracker row 'BluePeak Dental'. Status: on track. Priority: high. Account manager: Ariana Cole.",
                signals=[
                    "Account Manager: Ariana Cole",
                    "Tracker status: on track",
                    "Priority: High",
                    "Client health: 84",
                ],
            ),
            "client_2": ClientIntelligenceSnapshot(
                id="snapshot_2",
                source="ClickUp",
                synced_at="2026-06-16T09:05:00Z",
                sync_status="warning",
                clickup_task_id="task_2",
                clickup_task_name="Northwind Legal",
                clickup_task_url="https://app.clickup.com/t/task_2",
                account_manager=None,
                task_status="needs review",
                task_priority="Urgent",
                due_at=None,
                last_activity_at="2026-06-16T08:50:00Z",
                summary="Matched ClickUp tracker row 'Northwind Legal'. Status: needs review. Priority: urgent. Account manager is missing from the tracker row.",
                signals=[
                    "Tracker status: needs review",
                    "Priority: Urgent",
                    "Lead quality: Needs review",
                ],
            ),
        }

    def build_context(
        self,
        user_id: str | None,
        role_override: str | None,
        tenant_id_override: str | None = None,
        tenant_name_override: str | None = None,
        tenant_user_id_override: str | None = None,
    ) -> TenantContext:
        user = self._find_user(user_id or "user_1")
        if role_override in {"admin", "account_manager"}:
            user = user.model_copy(update={"role": role_override})

        return TenantContext(
            tenant_id=tenant_id_override or self.tenant_id,
            tenant_name=tenant_name_override or self.tenant_name,
            tenant_user_id=tenant_user_id_override or user.id,
            current_user=user,
        )

    def dashboard_overview(self, context: TenantContext) -> DashboardOverview:
        visible_clients = self.list_clients(context)
        visible_touches = self.list_monthly_touches(context)

        metrics = [
            MetricCard(
                id="briefs",
                label="Briefs Ready",
                value=str(max(len(visible_touches), 1) * 3),
                detail=f"{len(visible_touches)} visible Monthly Touch workflows",
                trend="up",
            ),
            MetricCard(
                id="risk",
                label="Retention Risks",
                value=str(sum(1 for client in visible_clients if client.risk_level != "Low")),
                detail="Visible at your current ownership scope",
                trend="down" if context.current_user.role == "admin" else "stable",
            ),
            MetricCard(
                id="approvals",
                label="Pending Approvals",
                value=str(max(2, len(visible_touches) * 2)),
                detail="Tasks and recap approvals requiring AM signoff",
                trend="stable",
            ),
            MetricCard(
                id="qa",
                label="QA Coverage",
                value="92%" if context.current_user.role == "admin" else "88%",
                detail="Last 30 day meeting audit coverage",
                trend="up",
            ),
        ]

        return DashboardOverview(
            tenant_name=context.tenant_name,
            current_user=context.current_user,
            metrics=metrics,
            clients=visible_clients,
            monthly_touches=visible_touches,
            prompt_templates=deepcopy(self._prompt_templates),
            activity=deepcopy(self._activity),
        )

    def list_clients(self, context: TenantContext) -> list[ClientRecord]:
        clients = deepcopy(self._clients)
        if context.current_user.role == "admin":
            return clients
        return [client for client in clients if client.owner == context.current_user.full_name]

    def list_monthly_touches(self, context: TenantContext) -> list[MonthlyTouchRecord]:
        touches = deepcopy(self._monthly_touches)
        if context.current_user.role == "admin":
            return touches
        return [touch for touch in touches if touch.owner == context.current_user.full_name]

    def get_client_workspace(self, context: TenantContext, client_id: str) -> ClientWorkspace:
        client = next((item for item in self.list_clients(context) if item.id == client_id), None)
        if client is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

        touches = [
            touch.model_copy()
            for touch in self.list_monthly_touches(context)
            if touch.client_name == client.name
        ]
        visibility_scope = (
            "Admin visibility includes all clients in the tenant."
            if context.current_user.role == "admin"
            else "Ownership filtering limits this workspace to your assigned clients."
        )

        return ClientWorkspace(
            client=client.model_copy(),
            monthly_touches=touches,
            intelligence_summary=(
                f"{client.name} is currently rated {client.risk_level.lower()} risk with "
                f"a health score of {client.health_score}/100. The strongest visible expansion angle is "
                f"{client.top_opportunity.lower()}."
            ),
            priority_actions=[
                f"Prepare the next Monthly Touch scheduled for {client.next_touch_at}.",
                f"Validate owner follow-through for the {client.top_opportunity.lower()} opportunity.",
                "Review open risks and confirm whether escalation or recap follow-up is needed.",
            ],
            visibility_scope=visibility_scope,
            intelligence_snapshot=self._intelligence_snapshots.get(client.id).model_copy()
            if client.id in self._intelligence_snapshots
            else None,
        )

    def sync_client_intelligence(self, context: TenantContext, client_id: str) -> ClientIntelligenceSnapshot:
        client = next((item for item in self.list_clients(context) if item.id == client_id), None)
        if client is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

        snapshot = self._intelligence_snapshots.get(client.id)
        if snapshot is None:
            snapshot = ClientIntelligenceSnapshot(
                id=f"snapshot_{client.id}",
                source="ClickUp",
                synced_at="2026-06-16T09:15:00Z",
                sync_status="not_found",
                clickup_task_id=None,
                clickup_task_name=None,
                clickup_task_url=None,
                account_manager=None,
                task_status=None,
                task_priority=None,
                due_at=None,
                last_activity_at=None,
                summary="No ClickUp Client Health Tracker task matched this MTOS client by external_ref or normalized client name.",
                signals=[
                    "Verify the MTOS client external_ref matches the ClickUp task ID.",
                    "If name fallback is required, keep the ClickUp tracker task name aligned with the MTOS client name.",
                ],
            )

        self._intelligence_snapshots[client.id] = snapshot.model_copy(update={"synced_at": datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")})
        return self._intelligence_snapshots[client.id].model_copy()

    def list_prompts(self) -> list[PromptTemplateRecord]:
        return deepcopy(self._prompt_templates)

    def get_ownership_sync_summary(self, context: TenantContext) -> OwnershipSyncSummary:
        self._assert_admin(context)
        return self._sync_summary.model_copy()

    def list_ownership_exceptions(self, context: TenantContext) -> list[OwnershipExceptionRecord]:
        self._assert_admin(context)
        return deepcopy(self._exceptions)

    def run_ownership_sync(self, context: TenantContext) -> OwnershipSyncRunResult:
        self._assert_admin(context)
        timestamp = datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        self._sync_summary = self._sync_summary.model_copy(update={"last_run_at": timestamp})
        return OwnershipSyncRunResult(
            status="completed",
            summary=self._sync_summary.model_copy(),
            exceptions=deepcopy(self._exceptions),
        )

    def _find_user(self, user_id: str) -> UserProfile:
        for user in self._users:
            if user.id == user_id:
                return user.model_copy()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown MTOS user")

    @staticmethod
    def _assert_admin(context: TenantContext) -> None:
        if context.current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access is required for ownership sync administration",
            )


repository = InMemoryMTOSRepository()


def get_repository() -> InMemoryMTOSRepository:
    return repository
