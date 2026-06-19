from copy import deepcopy
from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.models import (
    ActivityRecord,
    ClientIntelligenceSnapshot,
    ClientRecord,
    ClientWorkspace,
    ClickUpClientImportResult,
    ClickUpIntegrationStatus,
    DashboardOverview,
    IntegrationConnectionStatus,
    MetricCard,
    MonthlyTouchArtifact,
    MonthlyTouchChecklistItem,
    MonthlyTouchDetail,
    MonthlyTouchRecord,
    MonthlyTouchWorkflowStep,
    OwnershipExceptionRecord,
    OwnershipSyncRunResult,
    OwnershipSyncSummary,
    PromptActivationRequest,
    PromptTemplateRecord,
    PromptTemplateDetail,
    PromptVersionCreateRequest,
    PromptVersionRecord,
    PromptWorkflowAssignment,
    SyncCursorStatus,
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
                client_id="client_1",
                scheduled_at="Jun 18 · 11:00 AM",
                stage="Pre-Meeting Intelligence",
                owner="Ariana Cole",
            ),
            MonthlyTouchRecord(
                id="touch_2",
                client_name="Northwind Legal",
                client_id="client_2",
                scheduled_at="Jun 19 · 2:30 PM",
                stage="Task Approval",
                owner="Mila Grant",
            ),
            MonthlyTouchRecord(
                id="touch_3",
                client_name="Harbor Ortho",
                client_id="client_3",
                scheduled_at="Jun 20 · 9:00 AM",
                stage="QA Audit",
                owner="Ariana Cole",
            ),
            MonthlyTouchRecord(
                id="touch_4",
                client_name="Verdant Med Spa",
                client_id="client_4",
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
        self._prompt_versions = {
            "prompt_1": [
                PromptVersionRecord(
                    id="prompt_1_v11",
                    version_number=11,
                    system_prompt="You are Claude preparing a Monthly Touch brief for an existing client account. Focus on strategic clarity and concise prioritization.",
                    user_prompt="Using the provided client context, produce: executive summary, top 3 wins, top 2 issues, campaign analysis, strategic recommendations, and suggested client questions.",
                    is_active=False,
                    created_at="2026-06-01T09:00:00Z",
                ),
                PromptVersionRecord(
                    id="prompt_1_v12",
                    version_number=12,
                    system_prompt="You are Claude creating a Monthly Touch brief that helps an Account Manager prove value, reduce churn risk, and guide a strategic client conversation.",
                    user_prompt="Generate a Monthly Touch Brief with executive summary, wins, issues, analysis, recommendations, and engagement questions. Tie every section to client value and next actions.",
                    is_active=True,
                    created_at="2026-06-14T09:00:00Z",
                ),
            ],
            "prompt_2": [
                PromptVersionRecord(
                    id="prompt_2_v6",
                    version_number=6,
                    system_prompt="You turn meeting transcripts into department-ready task drafts without auto-submitting them.",
                    user_prompt="Extract clear department tickets from the transcript, group them by team, and keep every item in draft status pending AM approval.",
                    is_active=True,
                    created_at="2026-06-10T09:00:00Z",
                )
            ],
            "prompt_3": [
                PromptVersionRecord(
                    id="prompt_3_v4",
                    version_number=4,
                    system_prompt="You review account context for retention risk and expansion opportunity.",
                    user_prompt="Summarize churn signals, missed opportunities, and the strongest strategic recommendation for the next Monthly Touch.",
                    is_active=False,
                    created_at="2026-06-12T09:00:00Z",
                )
            ],
        }
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
        self._clickup_connection = IntegrationConnectionStatus(
            provider="ClickUp",
            source="Client Health Tracker",
            configured=True,
            health="connected",
            connected_at="2026-06-16T09:00:00Z",
            last_verified_at="2026-06-16T09:05:00Z",
            last_error=None,
        )
        self._ownership_cursor = SyncCursorStatus(
            key="ownership_sync",
            provider="ClickUp",
            source="Client Health Tracker",
            status="completed",
            last_synced_at="2026-06-16T09:05:00Z",
            last_cursor="page:0",
            records_seen=4,
            records_processed=4,
            last_error=None,
        )
        self._intelligence_cursor = SyncCursorStatus(
            key="client_intelligence",
            provider="ClickUp",
            source="Client Health Tracker",
            status="completed",
            last_synced_at="2026-06-16T09:05:00Z",
            last_cursor="client_2",
            records_seen=1,
            records_processed=1,
            last_error=None,
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

    def get_monthly_touch_detail(self, context: TenantContext, touch_id: str) -> MonthlyTouchDetail:
        touch = next((item for item in self.list_monthly_touches(context) if item.id == touch_id), None)
        if touch is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monthly Touch not found")

        client = next((item for item in self.list_clients(context) if item.id == touch.client_id), None)
        if client is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

        steps = self._build_touch_workflow_steps(touch.stage)
        checklist = self._build_meeting_checklist(touch.stage)

        return MonthlyTouchDetail(
            touch=touch.model_copy(),
            account_health_score=client.health_score,
            risk_level=client.risk_level,
            executive_summary=(
                f"{client.name} enters this Monthly Touch with a health score of {client.health_score}/100 and "
                f"{client.risk_level.lower()} account risk. The meeting should prove progress, address current "
                f"friction, and align the client around the next move in {client.top_opportunity.lower()}."
            ),
            top_wins=[
                f"Momentum is visible around {client.top_opportunity.lower()}, giving the AM a concrete growth story to anchor.",
                f"Ownership is assigned to {touch.owner}, so the meeting has a clear operator and follow-through path.",
                f"The account already has a defined Monthly Touch slot at {touch.scheduled_at}, keeping cadence intact.",
            ],
            key_issues=[
                f"{client.risk_level} risk means the meeting cannot stay tactical; it needs a clear value narrative.",
                "Post-meeting outputs still require AM approval before deployment, so handoff speed matters.",
            ],
            strategic_recommendations=[
                "Use the first five minutes to connect recent wins to business value, not just channel activity.",
                f"Treat {client.top_opportunity.lower()} as the featured growth path and ask the client what would make it actionable this month.",
                "Close with explicit owners, deadlines, and the next Monthly Touch date before ending the call.",
            ],
            suggested_questions=[
                f"What outcome would make the next 30 days feel like a real step forward for {client.name}?",
                "Which recent campaign change felt most valuable from the client side?",
                "What friction is the client still feeling that the team may not see inside the tools?",
            ],
            workflow_steps=steps,
            meeting_checklist=checklist,
            generated_artifacts=self._build_generated_artifacts(touch.stage, client),
            prompt_stack=self._build_prompt_stack(self.list_prompts()),
            next_action=next(step.detail for step in steps if step.status == "current"),
        )

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

        synced_at = datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        self._intelligence_snapshots[client.id] = snapshot.model_copy(update={"synced_at": synced_at})
        self._intelligence_cursor = self._intelligence_cursor.model_copy(
            update={
                "status": "completed",
                "last_synced_at": synced_at,
                "last_cursor": client.id,
                "records_seen": 1,
                "records_processed": 1,
                "last_error": None,
            }
        )
        return self._intelligence_snapshots[client.id].model_copy()

    def list_prompts(self) -> list[PromptTemplateRecord]:
        return deepcopy(self._prompt_templates)

    def get_prompt_detail(self, context: TenantContext, prompt_id: str) -> PromptTemplateDetail:
        self._assert_admin(context)
        template = next((item for item in self._prompt_templates if item.id == prompt_id), None)
        if template is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt template not found")
        versions = sorted(
            deepcopy(self._prompt_versions.get(prompt_id, [])),
            key=lambda item: item.version_number,
            reverse=True,
        )
        active_version = next((item for item in versions if item.is_active), None)
        return PromptTemplateDetail(
            template=template.model_copy(),
            active_version_id=active_version.id if active_version else None,
            versions=versions,
        )

    def create_prompt_version(
        self, context: TenantContext, prompt_id: str, payload: PromptVersionCreateRequest
    ) -> PromptTemplateDetail:
        self._assert_admin(context)
        template = next((item for item in self._prompt_templates if item.id == prompt_id), None)
        if template is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt template not found")
        versions = self._prompt_versions.setdefault(prompt_id, [])
        next_version_number = max((item.version_number for item in versions), default=0) + 1
        versions.append(
            PromptVersionRecord(
                id=f"{prompt_id}_v{next_version_number}",
                version_number=next_version_number,
                system_prompt=payload.system_prompt,
                user_prompt=payload.user_prompt,
                is_active=False,
                created_at=datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            )
        )
        template.version = f"v{next_version_number}"
        template.status = "Draft"
        return self.get_prompt_detail(context, prompt_id)

    def activate_prompt_version(
        self, context: TenantContext, prompt_id: str, payload: PromptActivationRequest
    ) -> PromptTemplateDetail:
        self._assert_admin(context)
        template = next((item for item in self._prompt_templates if item.id == prompt_id), None)
        if template is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt template not found")
        versions = self._prompt_versions.get(prompt_id, [])
        target = next((item for item in versions if item.id == payload.version_id), None)
        if target is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt version not found")
        self._prompt_versions[prompt_id] = [
            item.model_copy(update={"is_active": item.id == payload.version_id}) for item in versions
        ]
        template.version = f"v{target.version_number}"
        template.status = "Active"
        return self.get_prompt_detail(context, prompt_id)

    def get_ownership_sync_summary(self, context: TenantContext) -> OwnershipSyncSummary:
        self._assert_admin(context)
        return self._sync_summary.model_copy()

    def list_ownership_exceptions(self, context: TenantContext) -> list[OwnershipExceptionRecord]:
        self._assert_admin(context)
        return deepcopy(self._exceptions)

    def import_clickup_clients(self, context: TenantContext) -> ClickUpClientImportResult:
        self._assert_admin(context)
        return ClickUpClientImportResult(status="completed", tasks_seen=0, clients_upserted=0)

    def get_clickup_integration_status(self, context: TenantContext) -> ClickUpIntegrationStatus:
        self._assert_admin(context)
        return ClickUpIntegrationStatus(
            configured=self._clickup_connection.configured,
            base_url="https://api.clickup.com/api/v2",
            team_id="demo-team",
            list_id="demo-list",
            connection=self._clickup_connection.model_copy(),
            ownership_cursor=self._ownership_cursor.model_copy(),
            intelligence_cursor=self._intelligence_cursor.model_copy(),
        )

    def run_ownership_sync(self, context: TenantContext) -> OwnershipSyncRunResult:
        self._assert_admin(context)
        timestamp = datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        self._sync_summary = self._sync_summary.model_copy(update={"last_run_at": timestamp})
        self._clickup_connection = self._clickup_connection.model_copy(
            update={"health": "connected", "last_verified_at": timestamp, "last_error": None}
        )
        self._ownership_cursor = self._ownership_cursor.model_copy(
            update={
                "status": "completed",
                "last_synced_at": timestamp,
                "last_cursor": "page:0",
                "records_seen": len(self._clients),
                "records_processed": len(self._clients),
                "last_error": None,
            }
        )
        return OwnershipSyncRunResult(
            status="completed",
            summary=self._sync_summary.model_copy(),
            exceptions=deepcopy(self._exceptions),
        )

    def _build_touch_workflow_steps(self, current_stage: str) -> list[MonthlyTouchWorkflowStep]:
        sequence = [
            ("context_collection", "Context Collection", "Gemini compiles account context from connected systems."),
            ("brief_generation", "Brief Generation", "Claude turns the organized context into the Monthly Touch brief."),
            ("live_meeting", "Monthly Touch Meeting", "The AM runs the meeting with the brief and checklist."),
            ("meeting_analysis", "Meeting Analysis", "Claude reviews transcript, notes, and checklist completion."),
            ("ticket_creation", "Ticket Creation", "Draft department tickets and deliverables are prepared for review."),
            ("approval", "Approval", "The AM approves tickets, follow-up email, and action items."),
            ("deployment", "Deployment", "Approved outputs are sent and internal records are updated."),
        ]
        stage_to_position = {
            "Pre-Meeting Intelligence": 0,
            "Meeting Scheduled": 1,
            "Meeting Intelligence": 3,
            "Task Approval": 4,
            "Recap Approval": 5,
            "QA Audit": 6,
        }
        current_index = stage_to_position.get(current_stage, 0)
        steps: list[MonthlyTouchWorkflowStep] = []
        for index, (step_id, label, detail) in enumerate(sequence):
            status_value = "upcoming"
            if index < current_index:
                status_value = "complete"
            elif index == current_index:
                status_value = "current"
            steps.append(
                MonthlyTouchWorkflowStep(
                    id=step_id,
                    label=label,
                    status=status_value,
                    detail=detail,
                )
            )
        return steps

    def _build_meeting_checklist(self, current_stage: str) -> list[MonthlyTouchChecklistItem]:
        done_cutoff = {
            "Pre-Meeting Intelligence": 2,
            "Meeting Scheduled": 3,
            "Meeting Intelligence": 7,
            "Task Approval": 9,
            "Recap Approval": 10,
            "QA Audit": 11,
        }.get(current_stage, 2)
        items = [
            "Discussed 3 wins",
            "Discussed 2 issues",
            "Reviewed rankings and visibility",
            "Reviewed website progress",
            "Reviewed territory expansion",
            "Reviewed calls and lead quality",
            "Reviewed Google Ads performance",
            "Asked strategic questions",
            "Requested testimonial or referral opportunity",
            "Drafted post-meeting actions",
            "Prepared follow-up email",
            "Scheduled next Monthly Touch",
        ]
        return [
            MonthlyTouchChecklistItem(
                id=f"checklist_{index + 1}",
                label=label,
                status="done" if index < done_cutoff else "pending",
            )
            for index, label in enumerate(items)
        ]

    def _build_generated_artifacts(self, current_stage: str, client: ClientRecord) -> list[MonthlyTouchArtifact]:
        artifact_status = {
            "Pre-Meeting Intelligence": ("ready", "in_progress", "pending_approval"),
            "Meeting Scheduled": ("ready", "pending_approval", "pending_approval"),
            "Meeting Intelligence": ("ready", "ready", "pending_approval"),
            "Task Approval": ("ready", "ready", "pending_approval"),
            "Recap Approval": ("ready", "ready", "pending_approval"),
            "QA Audit": ("ready", "ready", "ready"),
        }.get(current_stage, ("ready", "in_progress", "pending_approval"))
        return [
            MonthlyTouchArtifact(
                id="brief",
                label="Monthly Touch Brief",
                status=artifact_status[0],
                detail=f"Prepared around {client.top_opportunity.lower()} and current account health.",
            ),
            MonthlyTouchArtifact(
                id="tickets",
                label="Department Ticket Drafts",
                status=artifact_status[1],
                detail="Draft tasks are held for AM review before they are sent to ClickUp.",
            ),
            MonthlyTouchArtifact(
                id="follow_up",
                label="Post-Meeting Follow-Up",
                status=artifact_status[2],
                detail="Summary email and action items remain human-approved before deployment.",
            ),
        ]

    def _build_prompt_stack(self, prompts: list[PromptTemplateRecord]) -> list[PromptWorkflowAssignment]:
        return [
            self._select_prompt_assignment(
                prompts,
                purpose="Brief Generation",
                detail="Controls how Claude structures the Monthly Touch brief before the meeting.",
                preferred_terms=["brief", "monthly touch"],
            ),
            self._select_prompt_assignment(
                prompts,
                purpose="Meeting Audit",
                detail="Controls how Claude evaluates meeting quality, coaching gaps, and client intelligence after the call.",
                preferred_terms=["audit", "retention"],
            ),
            self._select_prompt_assignment(
                prompts,
                purpose="Ticket Creation",
                detail="Controls how follow-up tickets are drafted and prepared for AM approval.",
                preferred_terms=["ticket", "follow-up"],
            ),
            self._select_prompt_assignment(
                prompts,
                purpose="Post-Meeting Email",
                detail="Controls how the follow-up recap and next-step email are prepared for deployment.",
                preferred_terms=["email", "follow-up", "recap"],
            ),
        ]

    def _select_prompt_assignment(
        self,
        prompts: list[PromptTemplateRecord],
        purpose: str,
        detail: str,
        preferred_terms: list[str],
    ) -> PromptWorkflowAssignment:
        matched = next(
            (
                prompt
                for prompt in prompts
                if any(term in f"{prompt.name} {prompt.category}".lower() for term in preferred_terms)
            ),
            None,
        )
        if matched is None:
            return PromptWorkflowAssignment(
                purpose=purpose,
                template_id=None,
                template_name="Not Configured",
                version="—",
                provider="Mixed",
                status="missing",
                detail=detail,
            )
        status_value = "active" if matched.status == "Active" else "fallback"
        return PromptWorkflowAssignment(
            purpose=purpose,
            template_id=matched.id,
            template_name=matched.name,
            version=matched.version,
            provider=matched.provider,
            status=status_value,
            detail=detail,
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
