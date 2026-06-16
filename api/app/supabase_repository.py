from fastapi import HTTPException, status

from app.models import (
    ClientRecord,
    DashboardOverview,
    MonthlyTouchRecord,
    OwnershipExceptionRecord,
    OwnershipSyncRunResult,
    OwnershipSyncSummary,
    PromptTemplateRecord,
    TenantContext,
    UserProfile,
)
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

        http = self._http(context_token=None)
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
        http = self._http(context.auth_token)
        rows = http.get(
            "ownership_sync_exceptions",
            params={
                "select": "id,client_name,external_account_manager,suggested_user_name,reason,status,last_seen_at",
                "tenant_id": f"eq.{context.tenant_id}",
                "status": "eq.open",
                "order": "last_seen_at.desc",
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

    def run_ownership_sync(self, context: TenantContext) -> OwnershipSyncRunResult:
        http = self._http(context.auth_token)
        run_rows = http.post(
            "ownership_sync_runs",
            json_body={
                "tenant_id": context.tenant_id,
                "provider": "ClickUp",
                "source": "Client Health Tracker",
                "cadence_minutes": 15,
                "matched_clients": 0,
                "unmatched_clients": 0,
                "status": "completed",
            },
        )

        summary = self.get_ownership_sync_summary(context)
        exceptions = self.list_ownership_exceptions(context)

        if run_rows:
            summary = summary.model_copy(update={"last_run_at": str(run_rows[0].get("started_at") or summary.last_run_at)})

        return OwnershipSyncRunResult(status="completed", summary=summary, exceptions=exceptions)

    def _http(self, auth_token: str | None) -> SupabaseHTTP:
        if auth_token and self._supabase_anon_key:
            return SupabaseHTTP(self._supabase_url, apikey=self._supabase_anon_key, auth_bearer=auth_token)
        return SupabaseHTTP(self._supabase_url, apikey=self._supabase_service_role_key)

