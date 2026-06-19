from fastapi import APIRouter, Depends

from app.config import settings
from app.dependencies import get_tenant_context
from app.integrations.clickup import ClickUpClient
from app.models import ClickUpClientImportResult, ClickUpIntegrationStatus, OwnershipSyncRunResult, TenantContext
from app.repository_selector import get_repository


router = APIRouter(prefix="/integrations/clickup", tags=["integrations"])


@router.get("/status", response_model=ClickUpIntegrationStatus)
async def clickup_status(
    context: TenantContext = Depends(get_tenant_context),
) -> ClickUpIntegrationStatus:
    return get_repository().get_clickup_integration_status(context)


@router.post("/ping")
async def clickup_ping() -> dict[str, str]:
    if not settings.clickup_api_token:
        return {"status": "not_configured"}
    ClickUpClient(api_token=settings.clickup_api_token, base_url=settings.clickup_base_url).ping()
    return {"status": "ok"}


@router.post("/import-clients", response_model=ClickUpClientImportResult)
def clickup_import_clients(
    context: TenantContext = Depends(get_tenant_context),
) -> ClickUpClientImportResult:
    return get_repository().import_clickup_clients(context)


@router.post("/ownership-sync", response_model=OwnershipSyncRunResult)
def clickup_ownership_sync(
    context: TenantContext = Depends(get_tenant_context),
) -> OwnershipSyncRunResult:
    return get_repository().run_ownership_sync(context)
