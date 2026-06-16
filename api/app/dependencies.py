from fastapi import Header

from app.models import TenantContext
from app.auth import decode_jwt_payload_unverified
from app.config import settings
from app.repository_selector import get_repository


async def get_tenant_context(
    authorization: str | None = Header(default=None),
    x_mtos_user_id: str | None = Header(default=None),
    x_mtos_role: str | None = Header(default=None),
    x_mtos_tenant_user_id: str | None = Header(default=None),
) -> TenantContext:
    repo = get_repository()
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        payload = decode_jwt_payload_unverified(token)
        context = repo.build_context(
            user_id=payload.get("sub") or x_mtos_user_id,
            role_override=payload.get("app_role") or x_mtos_role,
            tenant_id_override=payload.get("tenant_id"),
            tenant_user_id_override=x_mtos_tenant_user_id,
        )
        return context.model_copy(update={"auth_token": token})

    if settings.trust_demo_headers:
        return repo.build_context(
            user_id=x_mtos_user_id,
            role_override=x_mtos_role,
            tenant_user_id_override=x_mtos_tenant_user_id,
        )

    return repo.build_context(user_id=None, role_override=None)
