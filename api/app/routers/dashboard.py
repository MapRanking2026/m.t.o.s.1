from fastapi import APIRouter, Depends

from app.dependencies import get_tenant_context
from app.models import (
    ClientIntelligenceSnapshot,
    ClientRecord,
    ClientWorkspace,
    DashboardOverview,
    MonthlyTouchRecord,
    PromptTemplateRecord,
    TenantContext,
)
from app.repository_selector import get_repository


router = APIRouter(tags=["mtos"])


@router.get("/me")
async def me(context: TenantContext = Depends(get_tenant_context)) -> dict[str, str]:
    return {
        "id": context.current_user.id,
        "fullName": context.current_user.full_name,
        "role": context.current_user.role,
        "email": context.current_user.email,
        "tenantId": context.tenant_id,
        "tenantName": context.tenant_name,
    }


@router.get("/dashboard/overview", response_model=DashboardOverview)
async def dashboard_overview(context: TenantContext = Depends(get_tenant_context)) -> DashboardOverview:
    return get_repository().dashboard_overview(context)


@router.get("/clients", response_model=list[ClientRecord])
async def list_clients(context: TenantContext = Depends(get_tenant_context)) -> list[ClientRecord]:
    return get_repository().list_clients(context)


@router.get("/clients/{client_id}", response_model=ClientWorkspace)
async def get_client_workspace(client_id: str, context: TenantContext = Depends(get_tenant_context)) -> ClientWorkspace:
    return get_repository().get_client_workspace(context, client_id)


@router.post("/clients/{client_id}/intelligence/sync", response_model=ClientIntelligenceSnapshot)
async def sync_client_intelligence(
    client_id: str, context: TenantContext = Depends(get_tenant_context)
) -> ClientIntelligenceSnapshot:
    return get_repository().sync_client_intelligence(context, client_id)


@router.get("/monthly-touches", response_model=list[MonthlyTouchRecord])
async def list_monthly_touches(context: TenantContext = Depends(get_tenant_context)) -> list[MonthlyTouchRecord]:
    return get_repository().list_monthly_touches(context)


@router.get("/prompts", response_model=list[PromptTemplateRecord])
async def list_prompts() -> list[PromptTemplateRecord]:
    return get_repository().list_prompts()
