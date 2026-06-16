from fastapi import HTTPException, status

from app.config import settings
from app.repository import InMemoryMTOSRepository, get_repository as get_in_memory_repository
from app.supabase_repository import SupabaseMTOSRepository


def get_repository() -> InMemoryMTOSRepository | SupabaseMTOSRepository:
    if settings.repository_mode == "in_memory":
        return get_in_memory_repository()

    if settings.repository_mode == "supabase":
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase repository selected but Supabase credentials are missing",
            )
        return SupabaseMTOSRepository(
            supabase_url=settings.supabase_url,
            supabase_service_role_key=settings.supabase_service_role_key,
            supabase_anon_key=settings.supabase_anon_key,
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unknown repository mode",
    )

