import httpx
from fastapi import APIRouter

from app.config import settings
from app.models import RuntimeCheck, RuntimeStatus
from app.supabase_http import SupabaseHTTP


router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/runtime-status", response_model=RuntimeStatus)
async def runtime_status() -> RuntimeStatus:
    checks: list[RuntimeCheck] = [
        RuntimeCheck(
            key="repository_mode",
            label="Repository mode",
            status="ok",
            detail=f"API is currently using `{settings.repository_mode}` mode.",
        ),
        RuntimeCheck(
            key="demo_headers",
            label="Demo header support",
            status="warning" if settings.trust_demo_headers else "ok",
            detail=(
                "Demo headers are enabled for local development."
                if settings.trust_demo_headers
                else "Demo headers are disabled; use real auth tokens."
            ),
        ),
    ]

    clickup_configured = bool(settings.clickup_api_token and settings.clickup_list_id)
    checks.append(
        RuntimeCheck(
            key="clickup_config",
            label="ClickUp configuration",
            status="ok" if clickup_configured else "warning",
            detail="ClickUp token/list ID loaded." if clickup_configured else "Missing MTOS_CLICKUP_API_TOKEN or MTOS_CLICKUP_LIST_ID.",
        )
    )

    supabase_configured = bool(settings.supabase_url and settings.supabase_service_role_key)
    supabase_rls_ready = False
    recommended_next_step = "Apply Supabase migrations and seed data to complete Phase 1 cutover."

    if not supabase_configured:
        checks.append(
            RuntimeCheck(
                key="supabase_config",
                label="Supabase configuration",
                status="error" if settings.repository_mode == "supabase" else "warning",
                detail="Missing Supabase URL or service role key.",
            )
        )
    else:
        checks.append(
            RuntimeCheck(
                key="supabase_config",
                label="Supabase configuration",
                status="ok",
                detail="Supabase URL and service role key are loaded.",
            )
        )

        http = SupabaseHTTP(settings.supabase_url or "", apikey=settings.supabase_service_role_key or "")
        required_tables = ["tenants", "tenant_users", "clients", "client_ownership", "ownership_sync_runs"]
        table_probe_failed = False

        for table in required_tables:
            try:
                http.get(table, params={"select": "id", "limit": "1"})
                checks.append(
                    RuntimeCheck(
                        key=f"table_{table}",
                        label=f"Supabase table `{table}`",
                        status="ok",
                        detail="Table is reachable through PostgREST.",
                    )
                )
            except httpx.HTTPStatusError as error:
                table_probe_failed = True
                checks.append(
                    RuntimeCheck(
                        key=f"table_{table}",
                        label=f"Supabase table `{table}`",
                        status="error",
                        detail=f"Probe failed with HTTP {error.response.status_code}.",
                    )
                )
            except httpx.HTTPError as error:
                table_probe_failed = True
                checks.append(
                    RuntimeCheck(
                        key=f"table_{table}",
                        label=f"Supabase table `{table}`",
                        status="error",
                        detail=f"Probe failed: {error.__class__.__name__}.",
                    )
                )

        supabase_rls_ready = not table_probe_failed
        recommended_next_step = (
            "Switch MTOS_REPOSITORY_MODE to `supabase` and validate the app with seeded tenant data."
            if supabase_rls_ready
            else "Apply the MTOS SQL migrations in Supabase, then rerun the seed script."
        )

    return RuntimeStatus(
        environment=settings.environment,
        repository_mode=settings.repository_mode,
        trust_demo_headers=settings.trust_demo_headers,
        supabase_configured=supabase_configured,
        supabase_rls_ready=supabase_rls_ready,
        recommended_next_step=recommended_next_step,
        checks=checks,
    )
