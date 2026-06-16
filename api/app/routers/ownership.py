from fastapi import APIRouter, Depends

from app.dependencies import get_tenant_context
from app.models import OwnershipExceptionRecord, OwnershipSyncRunResult, OwnershipSyncSummary, TenantContext
from app.repository_selector import get_repository


router = APIRouter(prefix="/ownership", tags=["ownership"])


@router.get("/summary", response_model=OwnershipSyncSummary)
async def ownership_summary(
    context: TenantContext = Depends(get_tenant_context),
) -> OwnershipSyncSummary:
    return get_repository().get_ownership_sync_summary(context)


@router.get("/exceptions", response_model=list[OwnershipExceptionRecord])
async def ownership_exceptions(
    context: TenantContext = Depends(get_tenant_context),
) -> list[OwnershipExceptionRecord]:
    return get_repository().list_ownership_exceptions(context)


@router.post("/sync", response_model=OwnershipSyncRunResult)
async def run_ownership_sync(
    context: TenantContext = Depends(get_tenant_context),
) -> OwnershipSyncRunResult:
    return get_repository().run_ownership_sync(context)
