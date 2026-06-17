import httpx
from fastapi import HTTPException, status

from app.config import settings
from app.integrations.clickup import ClickUpClient
from app.models import (
    ClientIntelligenceSnapshot,
    ClientRecord,
    ClientWorkspace,
    ClickUpIntegrationStatus,
    DashboardOverview,
    IntegrationConnectionStatus,
    MonthlyTouchRecord,
    OwnershipExceptionRecord,
    OwnershipSyncRunResult,
    OwnershipSyncSummary,
    PromptTemplateRecord,
    SyncCursorStatus,
    TenantContext,
    UserProfile,
)
from app.services.client_intelligence_sync import ClientIntelligenceSyncConfig, ClientIntelligenceSyncService
from app.services.ownership_sync import OwnershipSyncConfig, OwnershipSyncService
from app.supabase_http import SupabaseHTTP


class SupabaseMTOSRepository:
    def __init__(
        self,
        supabase_url: str,
        supabase_service_role_key: str,
        supabase_anon_key: str | None = None,
    ) -> None:
        self._supabase_url = supabase_url
        self._supabase_service_role_key = supabase_service_role_key
        self._supabase_anon_key = supabase_anon_key

    def build_context(
        self,
        user_id: str | None,
        role_override: str | None,
        tenant_id_override: str | None = None,
        tenant_name_override: str | None = None,
        tenant_user_id_override: str | None = None,
    ) -> TenantContext:
        if not user_id and not role_override:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authenticated user context")

        http = self._http(None)
        if tenant_user_id_override:
            membership = http.get(
                "tenant_users",
                params={
                    "select": "id,tenant_id,full_name,role,auth_user_id",
                    "id": f"eq.{tenant_user_id_override}",
                    "limit": "1",
                },
            )
        else:
            membership = http.get(
                "tenant_users",
                params={
                    "select": "id,tenant_id,full_name,role,auth_user_id",
                    "auth_user_id": f"eq.{user_id}" if user_id else "is.null",
                    "limit": "1",
                },
            )

        auth_user_id = membership[0].get("auth_user_id") if membership else None
        tenant_id = tenant_id_override or (membership[0]["tenant_id"] if membership else None)
        if not tenant_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No tenant membership found")

        tenant_rows = http.get(
            "tenants",
            params={"select": "name", "id": f"eq.{tenant_id}", "limit": "1"},
        )

        tenant_name = tenant_name_override or (tenant_rows[0]["name"] if tenant_rows else "MTOS Tenant")
        full_name = membership[0].get("full_name") if membership else "MTOS User"
        resolved_role = membership[0].get("role") if membership else (role_override or "account_manager")
        tenant_user_id = membership[0].get("id") if membership else tenant_user_id_override

        return TenantContext(
            tenant_id=str(tenant_id),
            tenant_name=tenant_name,
            tenant_user_id=str(tenant_user_id) if tenant_user_id else None,
            current_user=UserProfile(
                id=str(auth_user_id or user_id or ""),
                full_name=full_name,
                role=resolved_role,
                email="user@mtos.com",
            ),
        )

    def dashboard_overview(self, context: TenantContext) -> DashboardOverview:
        clients = self.list_clients(context)
        monthly_touches = self.list_monthly_touches(context)

        metrics = [
            {
                "id": "briefs",
                "label": "Briefs Ready",
                "value": str(max(len(monthly_touches), 1) * 3),
                "detail": f"{len(monthly_touches)} visible Monthly Touch workflows",
                "trend": "up",
            },
            {
                "id": "risk",
                "label": "Retention Risks",
                "value": str(sum(1 for client in clients if client.risk_level != "Low")),
                "detail": "Visible at your current ownership scope",
                "trend": "down" if context.current_user.role == "admin" else "stable",
            },
            {
                "id": "approvals",
                "label": "Pending Approvals",
                "value": str(max(2, len(monthly_touches) * 2)),
                "detail": "Tasks and recap approvals requiring AM signoff",
                "trend": "stable",
            },
            {
                "id": "qa",
                "label": "QA Coverage",
                "value": "92%" if context.current_user.role == "admin" else "88%",
                "detail": "Last 30 day meeting audit coverage",
                "trend": "up",
            },
        ]

        return DashboardOverview.model_validate(
            {
                "tenantName": context.tenant_name,
                "currentUser": context.current_user.model_dump(by_alias=True),
                "metrics": metrics,
                "clients": [client.model_dump(by_alias=True) for client in clients],
                "monthlyTouches": [touch.model_dump(by_alias=True) for touch in monthly_touches],
                "promptTemplates": [prompt.model_dump(by_alias=True) for prompt in self.list_prompts()],
                "activity": [],
            }
        )

    def list_clients(self, context: TenantContext) -> list[ClientRecord]:
        http = self._http(context.auth_token)
        clients = http.get(
            "clients",
            params={
                "select": "id,name,health_score,risk_level,next_touch_at,top_opportunity",
                "tenant_id": f"eq.{context.tenant_id}",
                "order": "name.asc",
            },
        )

        ownership_rows = http.get(
            "client_ownership",
            params={
                "select": "client_id,user_id,active",
                "tenant_id": f"eq.{context.tenant_id}",
                "active": "eq.true",
            },
        )

        user_ids = {row["user_id"] for row in ownership_rows if row.get("user_id")}
        users = (
            http.get(
                "tenant_users",
                params={
                    "select": "id,full_name,auth_user_id",
                    "tenant_id": f"eq.{context.tenant_id}",
                },
            )
            if user_ids
            else []
        )

        user_name_by_id = {user["id"]: user["full_name"] for user in users}
        owner_by_client_id = {row["client_id"]: user_name_by_id.get(row["user_id"], "Unassigned") for row in ownership_rows}

        if context.current_user.role != "admin":
            if not context.tenant_user_id:
                return []
            allowed_client_ids = {row["client_id"] for row in ownership_rows if row["user_id"] == context.tenant_user_id}
            clients = [client for client in clients if client["id"] in allowed_client_ids]

        return [
            ClientRecord(
                id=client["id"],
                name=client["name"],
                owner=owner_by_client_id.get(client["id"], "Unassigned"),
                health_score=client.get("health_score") or 0,
                risk_level=client.get("risk_level") or "Low",
                next_touch_at=client.get("next_touch_at") or "Not scheduled",
                top_opportunity=client.get("top_opportunity") or "—",
            )
            for client in clients
        ]

    def list_monthly_touches(self, context: TenantContext) -> list[MonthlyTouchRecord]:
        http = self._http(context.auth_token)
        touches = http.get(
            "monthly_touches",
            params={
                "select": "id,scheduled_at,stage,client_id",
                "tenant_id": f"eq.{context.tenant_id}",
                "order": "scheduled_at.asc",
                "limit": "12",
            },
        )

        clients = http.get(
            "clients",
            params={
                "select": "id,name",
                "tenant_id": f"eq.{context.tenant_id}",
            },
        )
        name_by_client_id = {client["id"]: client["name"] for client in clients}

        ownership_rows = http.get(
            "client_ownership",
            params={
                "select": "client_id,user_id",
                "tenant_id": f"eq.{context.tenant_id}",
                "active": "eq.true",
            },
        )
        users = http.get(
            "tenant_users",
            params={
                "select": "id,full_name,auth_user_id",
                "tenant_id": f"eq.{context.tenant_id}",
            },
        )
        user_name_by_id = {user["id"]: user["full_name"] for user in users}
        owner_by_client_id = {row["client_id"]: user_name_by_id.get(row["user_id"], "Unassigned") for row in ownership_rows}

        if context.current_user.role != "admin":
            if not context.tenant_user_id:
                return []
            allowed_client_ids = {row["client_id"] for row in ownership_rows if row["user_id"] == context.tenant_user_id}
            touches = [touch for touch in touches if touch["client_id"] in allowed_client_ids]

        return [
            MonthlyTouchRecord(
                id=touch["id"],
                client_name=name_by_client_id.get(touch["client_id"], "Client"),
                scheduled_at=str(touch["scheduled_at"]),
                stage=touch.get("stage") or "Meeting Scheduled",
                owner=owner_by_client_id.get(touch["client_id"], "Unassigned"),
            )
            for touch in touches
        ]

    def get_client_workspace(self, context: TenantContext, client_id: str) -> ClientWorkspace:
        client = next((item for item in self.list_clients(context) if item.id == client_id), None)
        if client is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

        http = self._http(context.auth_token)
        touches = http.get(
            "monthly_touches",
            params={
                "select": "id,scheduled_at,stage,client_id",
                "tenant_id": f"eq.{context.tenant_id}",
                "client_id": f"eq.{client_id}",
                "order": "scheduled_at.desc",
                "limit": "8",
            },
        )

        monthly_touches = [
            MonthlyTouchRecord(
                id=touch["id"],
                client_name=client.name,
                scheduled_at=str(touch["scheduled_at"]),
                stage=touch.get("stage") or "Meeting Scheduled",
                owner=client.owner,
            )
            for touch in touches
        ]
        visibility_scope = (
            "Admin visibility includes all clients in the tenant."
            if context.current_user.role == "admin"
            else "Ownership filtering limits this workspace to your assigned clients."
        )
        snapshot = self._latest_client_intelligence_snapshot(context=context, client_id=client_id)

        return ClientWorkspace(
            client=client.model_copy(),
            monthly_touches=monthly_touches,
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
            intelligence_snapshot=snapshot,
        )

    def list_prompts(self) -> list[PromptTemplateRecord]:
        http = self._http(None)
        templates = http.get(
            "prompt_templates",
            params={
                "select": "id,name,category,status,provider,active_version",
                "order": "category.asc,name.asc",
                "limit": "50",
            },
        )

        return [
            PromptTemplateRecord(
                id=row["id"],
                name=row["name"],
                category=row["category"],
                version=row.get("active_version") or "v1",
                status=(row.get("status") or "Draft").title(),
                provider=(row.get("provider") or "Mixed"),
            )
            for row in templates
        ]

    def get_ownership_sync_summary(self, context: TenantContext) -> OwnershipSyncSummary:
        self._assert_admin(context)
        http = self._http(context.auth_token)
        runs = http.get(
            "ownership_sync_runs",
            params={
                "select": "provider,source,cadence_minutes,started_at,matched_clients,unmatched_clients",
                "tenant_id": f"eq.{context.tenant_id}",
                "order": "started_at.desc",
                "limit": "1",
            },
        )
        exceptions = self.list_ownership_exceptions(context)

        if not runs:
            return OwnershipSyncSummary(
                provider="ClickUp",
                source="Client Health Tracker",
                cadence_minutes=15,
                last_run_at="Never",
                matched_clients=0,
                unmatched_clients=0,
                exception_count=len(exceptions),
            )

        run = runs[0]
        return OwnershipSyncSummary(
            provider=run["provider"],
            source=run["source"],
            cadence_minutes=run.get("cadence_minutes") or 15,
            last_run_at=str(run["started_at"]),
            matched_clients=run.get("matched_clients") or 0,
            unmatched_clients=run.get("unmatched_clients") or 0,
            exception_count=len(exceptions),
        )

    def list_ownership_exceptions(self, context: TenantContext) -> list[OwnershipExceptionRecord]:
        self._assert_admin(context)
        http = self._http(context.auth_token)
        rows = http.get(
            "ownership_sync_exceptions",
            params={
                "select": "id,client_name,external_account_manager,suggested_user_name,reason,status,last_seen_at",
                "tenant_id": f"eq.{context.tenant_id}",
                "status": "eq.open",
                "order": "last_seen_at.desc",
                "limit": "50",
            },
        )

        return [
            OwnershipExceptionRecord(
                id=row["id"],
                client_name=row["client_name"],
                external_account_manager=row["external_account_manager"],
                suggested_user_name=row.get("suggested_user_name"),
                reason=row["reason"],
                status=row.get("status") or "open",
                last_seen_at=str(row["last_seen_at"]),
            )
            for row in rows
        ]

    def get_clickup_integration_status(self, context: TenantContext) -> ClickUpIntegrationStatus:
        self._assert_admin(context)
        configured = bool(settings.clickup_api_token and settings.clickup_list_id)
        connection = self._integration_connection(context.tenant_id, provider="clickup", source="client_health_tracker")
        ownership_cursor = self._sync_cursor(context.tenant_id, "clickup", "client_health_tracker", "ownership_sync")
        intelligence_cursor = self._sync_cursor(
            context.tenant_id,
            "clickup",
            "client_health_tracker",
            "client_intelligence",
        )

        return ClickUpIntegrationStatus(
            configured=configured,
            base_url=settings.clickup_base_url,
            team_id=settings.clickup_team_id,
            list_id=settings.clickup_list_id,
            connection=connection,
            ownership_cursor=ownership_cursor,
            intelligence_cursor=intelligence_cursor,
        )

    def run_ownership_sync(self, context: TenantContext) -> OwnershipSyncRunResult:
        self._assert_admin(context)
        if not settings.clickup_api_token or not settings.clickup_list_id:
            self._upsert_integration_connection(
                tenant_id=context.tenant_id,
                provider="clickup",
                source="client_health_tracker",
                configured=False,
                health="not_configured",
                last_error="Missing MTOS_CLICKUP_API_TOKEN or MTOS_CLICKUP_LIST_ID.",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ClickUp integration is not configured (missing MTOS_CLICKUP_API_TOKEN or MTOS_CLICKUP_LIST_ID).",
            )

        http = self._http(context.auth_token)
        self._upsert_integration_connection(
            tenant_id=context.tenant_id,
            provider="clickup",
            source="client_health_tracker",
            configured=True,
            health="connected",
            last_error=None,
        )
        self._upsert_sync_cursor(
            tenant_id=context.tenant_id,
            provider="clickup",
            source="client_health_tracker",
            key="ownership_sync",
            status_value="running",
            last_cursor="page:0",
            records_seen=0,
            records_processed=0,
            last_error=None,
        )
        clickup = ClickUpClient(
            api_token=settings.clickup_api_token,
            base_url=settings.clickup_base_url,
        )
        sync = OwnershipSyncService(
            http=http,
            clickup=clickup,
            config=OwnershipSyncConfig(
                clickup_list_id=settings.clickup_list_id,
                clickup_am_custom_field_id=settings.clickup_am_custom_field_id,
                clickup_include_closed=settings.clickup_include_closed,
                clickup_max_pages=settings.clickup_max_pages,
                clickup_max_tasks=settings.clickup_max_tasks,
            ),
        )
        try:
            result = sync.run(tenant_id=context.tenant_id)
        except HTTPException as exc:
            error_text = str(exc.detail) if hasattr(exc, "detail") else str(exc)
            self._upsert_integration_connection(
                tenant_id=context.tenant_id,
                provider="clickup",
                source="client_health_tracker",
                configured=True,
                health="warning",
                last_error=error_text,
            )
            self._upsert_sync_cursor(
                tenant_id=context.tenant_id,
                provider="clickup",
                source="client_health_tracker",
                key="ownership_sync",
                status_value="error",
                last_cursor="page:0",
                records_seen=0,
                records_processed=0,
                last_error=error_text,
            )
            raise

        self._upsert_sync_cursor(
            tenant_id=context.tenant_id,
            provider="clickup",
            source="client_health_tracker",
            key="ownership_sync",
            status_value="completed",
            last_cursor=f"page:{max(settings.clickup_max_pages - 1, 0)}",
            records_seen=result["matched_clients"] + result["unmatched_clients"],
            records_processed=result["matched_clients"],
            last_error=None,
        )

        summary = self.get_ownership_sync_summary(context)
        return OwnershipSyncRunResult(status="completed", summary=summary, exceptions=[])

    def sync_client_intelligence(self, context: TenantContext, client_id: str) -> ClientIntelligenceSnapshot:
        if not settings.clickup_api_token or not settings.clickup_list_id:
            self._upsert_integration_connection(
                tenant_id=context.tenant_id,
                provider="clickup",
                source="client_health_tracker",
                configured=False,
                health="not_configured",
                last_error="Missing MTOS_CLICKUP_API_TOKEN or MTOS_CLICKUP_LIST_ID.",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ClickUp integration is not configured (missing MTOS_CLICKUP_API_TOKEN or MTOS_CLICKUP_LIST_ID).",
            )

        client_row = self._client_row_for_context(context=context, client_id=client_id)
        self._upsert_integration_connection(
            tenant_id=context.tenant_id,
            provider="clickup",
            source="client_health_tracker",
            configured=True,
            health="connected",
            last_error=None,
        )
        self._upsert_sync_cursor(
            tenant_id=context.tenant_id,
            provider="clickup",
            source="client_health_tracker",
            key="client_intelligence",
            status_value="running",
            last_cursor=client_id,
            records_seen=0,
            records_processed=0,
            last_error=None,
        )
        sync = ClientIntelligenceSyncService(
            http=self._http(None),
            clickup=ClickUpClient(
                api_token=settings.clickup_api_token,
                base_url=settings.clickup_base_url,
            ),
            config=ClientIntelligenceSyncConfig(
                clickup_list_id=settings.clickup_list_id,
                clickup_am_custom_field_id=settings.clickup_am_custom_field_id,
                clickup_include_closed=settings.clickup_include_closed,
                clickup_max_pages=settings.clickup_max_pages,
                clickup_max_tasks=settings.clickup_max_tasks,
            ),
        )
        try:
            snapshot = sync.sync_client(tenant_id=context.tenant_id, client_row=client_row)
        except HTTPException as exc:
            error_text = str(exc.detail) if hasattr(exc, "detail") else str(exc)
            self._upsert_integration_connection(
                tenant_id=context.tenant_id,
                provider="clickup",
                source="client_health_tracker",
                configured=True,
                health="warning",
                last_error=error_text,
            )
            self._upsert_sync_cursor(
                tenant_id=context.tenant_id,
                provider="clickup",
                source="client_health_tracker",
                key="client_intelligence",
                status_value="error",
                last_cursor=client_id,
                records_seen=0,
                records_processed=0,
                last_error=error_text,
            )
            raise

        self._upsert_sync_cursor(
            tenant_id=context.tenant_id,
            provider="clickup",
            source="client_health_tracker",
            key="client_intelligence",
            status_value="completed",
            last_synced_at=snapshot.synced_at,
            last_cursor=snapshot.clickup_task_id or client_id,
            records_seen=1,
            records_processed=1,
            last_error=None,
        )
        return snapshot

    def _http(self, auth_token: str | None) -> SupabaseHTTP:
        if auth_token and self._supabase_anon_key:
            return SupabaseHTTP(self._supabase_url, apikey=self._supabase_anon_key, auth_bearer=auth_token)
        return SupabaseHTTP(self._supabase_url, apikey=self._supabase_service_role_key)

    def _client_row_for_context(self, context: TenantContext, client_id: str) -> dict[str, str]:
        client = next((item for item in self.list_clients(context) if item.id == client_id), None)
        if client is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

        rows = self._http(None).get(
            "clients",
            params={
                "select": "id,name,external_ref",
                "tenant_id": f"eq.{context.tenant_id}",
                "id": f"eq.{client_id}",
                "limit": "1",
            },
        )
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
        return rows[0]

    def _latest_client_intelligence_snapshot(
        self, context: TenantContext, client_id: str
    ) -> ClientIntelligenceSnapshot | None:
        try:
            rows = self._http(None).get(
                "client_intelligence_snapshots",
                params={
                    "select": "id,source,sync_status,clickup_task_id,clickup_task_name,clickup_task_url,account_manager,task_status,task_priority,due_at,last_activity_at,summary,signals_json,synced_at",
                    "tenant_id": f"eq.{context.tenant_id}",
                    "client_id": f"eq.{client_id}",
                    "source": "eq.clickup",
                    "order": "synced_at.desc",
                    "limit": "1",
                },
            )
        except httpx.HTTPStatusError:
            return None
        if not rows:
            return None

        row = rows[0]
        return ClientIntelligenceSnapshot(
            id=str(row["id"]),
            source=str(row.get("source") or "clickup").title(),
            synced_at=str(row.get("synced_at") or ""),
            sync_status=str(row.get("sync_status") or "not_found"),
            clickup_task_id=str(row.get("clickup_task_id")) if row.get("clickup_task_id") else None,
            clickup_task_name=str(row.get("clickup_task_name")) if row.get("clickup_task_name") else None,
            clickup_task_url=str(row.get("clickup_task_url")) if row.get("clickup_task_url") else None,
            account_manager=str(row.get("account_manager")) if row.get("account_manager") else None,
            task_status=str(row.get("task_status")) if row.get("task_status") else None,
            task_priority=str(row.get("task_priority")).title() if row.get("task_priority") else None,
            due_at=str(row.get("due_at")) if row.get("due_at") else None,
            last_activity_at=str(row.get("last_activity_at")) if row.get("last_activity_at") else None,
            summary=str(row.get("summary") or ""),
            signals=[str(item) for item in list(row.get("signals_json") or []) if str(item).strip()],
        )

    def _integration_connection(
        self, tenant_id: str, provider: str, source: str
    ) -> IntegrationConnectionStatus | None:
        try:
            rows = self._http(None).get(
                "integration_connections",
                params={
                    "select": "provider,source,configured,health,connected_at,last_verified_at,last_error",
                    "tenant_id": f"eq.{tenant_id}",
                    "provider": f"eq.{provider}",
                    "source": f"eq.{source}",
                    "limit": "1",
                },
            )
        except httpx.HTTPStatusError:
            return None
        if not rows:
            return None

        row = rows[0]
        return IntegrationConnectionStatus(
            provider=str(row.get("provider") or provider).title(),
            source=str(row.get("source") or source).replace("_", " ").title(),
            configured=bool(row.get("configured")),
            health=str(row.get("health") or "not_configured"),
            connected_at=str(row.get("connected_at")) if row.get("connected_at") else None,
            last_verified_at=str(row.get("last_verified_at")) if row.get("last_verified_at") else None,
            last_error=str(row.get("last_error")) if row.get("last_error") else None,
        )

    def _sync_cursor(self, tenant_id: str, provider: str, source: str, key: str) -> SyncCursorStatus | None:
        try:
            rows = self._http(None).get(
                "sync_cursors",
                params={
                    "select": "cursor_key,provider,source,status,last_synced_at,last_cursor,records_seen,records_processed,last_error",
                    "tenant_id": f"eq.{tenant_id}",
                    "provider": f"eq.{provider}",
                    "source": f"eq.{source}",
                    "cursor_key": f"eq.{key}",
                    "limit": "1",
                },
            )
        except httpx.HTTPStatusError:
            return None
        if not rows:
            return None

        row = rows[0]
        return SyncCursorStatus(
            key=str(row.get("cursor_key") or key),
            provider=str(row.get("provider") or provider).title(),
            source=str(row.get("source") or source).replace("_", " ").title(),
            status=str(row.get("status") or "idle"),
            last_synced_at=str(row.get("last_synced_at")) if row.get("last_synced_at") else None,
            last_cursor=str(row.get("last_cursor")) if row.get("last_cursor") else None,
            records_seen=int(row.get("records_seen") or 0),
            records_processed=int(row.get("records_processed") or 0),
            last_error=str(row.get("last_error")) if row.get("last_error") else None,
        )

    def _upsert_integration_connection(
        self,
        tenant_id: str,
        provider: str,
        source: str,
        configured: bool,
        health: str,
        last_error: str | None,
    ) -> None:
        now = self._now_iso()
        payload = {
            "tenant_id": tenant_id,
            "provider": provider,
            "source": source,
            "configured": configured,
            "health": health,
            "last_verified_at": now,
            "last_error": last_error,
        }
        existing = self._integration_connection(tenant_id, provider=provider, source=source)
        if configured and health == "connected":
            payload["connected_at"] = existing.connected_at if existing and existing.connected_at else now
        try:
            self._http(None).upsert(
                "integration_connections",
                json_body=payload,
                on_conflict="tenant_id,provider,source",
            )
        except httpx.HTTPStatusError:
            return

    def _upsert_sync_cursor(
        self,
        tenant_id: str,
        provider: str,
        source: str,
        key: str,
        status_value: str,
        last_cursor: str | None,
        records_seen: int,
        records_processed: int,
        last_error: str | None,
        last_synced_at: str | None = None,
    ) -> None:
        payload = {
            "tenant_id": tenant_id,
            "provider": provider,
            "source": source,
            "cursor_key": key,
            "status": status_value,
            "last_cursor": last_cursor,
            "records_seen": records_seen,
            "records_processed": records_processed,
            "last_error": last_error,
        }
        if last_synced_at:
            payload["last_synced_at"] = last_synced_at
        elif status_value == "completed":
            payload["last_synced_at"] = self._now_iso()
        try:
            self._http(None).upsert(
                "sync_cursors",
                json_body=payload,
                on_conflict="tenant_id,provider,source,cursor_key",
            )
        except httpx.HTTPStatusError:
            return

    @staticmethod
    def _now_iso() -> str:
        from datetime import UTC, datetime

        return datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _assert_admin(context: TenantContext) -> None:
        if context.current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access is required for ownership sync administration",
            )

