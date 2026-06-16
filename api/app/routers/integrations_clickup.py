from fastapi import APIRouter, Depends

from app.config import settings
from app.dependencies import get_tenant_context
from app.integrations.clickup import ClickUpClient
from app.models import ClickUpIntegrationStatus, OwnershipSyncRunResult, TenantContext
from app.repository_selector import get_repository


router = APIRouter(prefix="/integrations/clickup", tags=["integrations"])


@router.get("/status", response_model=ClickUpIntegrationStatus)
async def clickup_status() -> ClickUpIntegrationStatus:
    configured = bool(settings.clickup_api_token and settings.clickup_list_id)
    return ClickUpIntegrationStatus(
        configured=configured,
        base_url=settings.clickup_base_url,
        team_id=settings.clickup_team_id,
        list_id=settings.clickup_list_id,
    )


@router.post("/ping")
async def clickup_ping() -> dict[str, str]:
    if not settings.clickup_api_token:
        return {"status": "not_configured"}
    ClickUpClient(api_token=settings.clickup_api_token, base_url=settings.clickup_base_url).ping()
    return {"status": "ok"}


@router.post("/ownership-sync", response_model=OwnershipSyncRunResult)
def clickup_ownership_sync(
    context: TenantContext = Depends(get_tenant_context),
) -> OwnershipSyncRunResult:
    return get_repository().run_ownership_sync(context)
