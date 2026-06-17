import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import httpx

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.supabase_http import SupabaseHTTP


def load_env_files(paths: list[str]) -> None:
    for path in paths:
        try:
            with open(path, encoding="utf-8") as file:
                for raw_line in file:
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ.setdefault(key, value)
        except FileNotFoundError:
            continue


def must_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> None:
    load_env_files([".env", ".env.local", "../.env", "../.env.local"])
    supabase_url = must_env("MTOS_SUPABASE_URL")
    service_role_key = must_env("MTOS_SUPABASE_SERVICE_ROLE_KEY")

    http = SupabaseHTTP(supabase_url, apikey=service_role_key)

    tenant_id = UUID(must_env("MTOS_SEED_TENANT_ID"))
    tenant_slug = must_env("MTOS_SEED_TENANT_SLUG")
    tenant_name = must_env("MTOS_SEED_TENANT_NAME")

    try:
        http.upsert(
            "tenants",
            json_body={"id": str(tenant_id), "name": tenant_name, "slug": tenant_slug, "status": "active"},
            on_conflict="slug",
        )
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 404:
            raise RuntimeError(
                "Supabase REST API returned 404 for the 'tenants' table. "
                "This usually means the migrations have not been applied yet in Supabase (table does not exist or is not exposed). "
                "Apply the SQL migrations in supabase/migrations and retry."
            ) from error
        raise

    admin_tenant_user_id = UUID("22222222-2222-2222-2222-222222222222")
    am1_tenant_user_id = UUID("33333333-3333-3333-3333-333333333333")
    am2_tenant_user_id = UUID("44444444-4444-4444-4444-444444444444")

    http.upsert(
        "tenant_users",
        json_body=[
            {
                "id": str(admin_tenant_user_id),
                "tenant_id": str(tenant_id),
                "auth_user_id": str(uuid4()),
                "full_name": "Ariana Cole",
                "role": "admin",
            },
            {
                "id": str(am1_tenant_user_id),
                "tenant_id": str(tenant_id),
                "auth_user_id": str(uuid4()),
                "full_name": "Mila Grant",
                "role": "account_manager",
            },
            {
                "id": str(am2_tenant_user_id),
                "tenant_id": str(tenant_id),
                "auth_user_id": str(uuid4()),
                "full_name": "Leo Parker",
                "role": "account_manager",
            },
        ],
        on_conflict="id",
    )

    clients = [
        {
            "id": "55555555-5555-5555-5555-555555555555",
            "tenant_id": str(tenant_id),
            "name": "BluePeak Dental",
            "health_score": 84,
            "risk_level": "Low",
            "next_touch_at": "Jun 18 · 11:00 AM",
            "top_opportunity": "GBP optimization",
        },
        {
            "id": "66666666-6666-6666-6666-666666666666",
            "tenant_id": str(tenant_id),
            "name": "Northwind Legal",
            "health_score": 67,
            "risk_level": "Medium",
            "next_touch_at": "Jun 19 · 2:30 PM",
            "top_opportunity": "Lead qualification automation",
        },
        {
            "id": "77777777-7777-7777-7777-777777777777",
            "tenant_id": str(tenant_id),
            "name": "Harbor Ortho",
            "health_score": 51,
            "risk_level": "High",
            "next_touch_at": "Jun 20 · 9:00 AM",
            "top_opportunity": "Retention rescue plan",
        },
        {
            "id": "88888888-8888-8888-8888-888888888888",
            "tenant_id": str(tenant_id),
            "name": "Verdant Med Spa",
            "health_score": 76,
            "risk_level": "Low",
            "next_touch_at": "Jun 21 · 1:30 PM",
            "top_opportunity": "Paid social expansion",
        },
    ]

    http.upsert("clients", json_body=clients, on_conflict="id")

    ownership = [
        {
            "id": "c0c0c0c0-c0c0-c0c0-c0c0-c0c0c0c0c0c0",
            "tenant_id": str(tenant_id),
            "client_id": clients[0]["id"],
            "user_id": str(admin_tenant_user_id),
            "active": True,
        },
        {
            "id": "d0d0d0d0-d0d0-d0d0-d0d0-d0d0d0d0d0d0",
            "tenant_id": str(tenant_id),
            "client_id": clients[1]["id"],
            "user_id": str(am1_tenant_user_id),
            "active": True,
        },
        {
            "id": "e0e0e0e0-e0e0-e0e0-e0e0-e0e0e0e0e0e0",
            "tenant_id": str(tenant_id),
            "client_id": clients[2]["id"],
            "user_id": str(admin_tenant_user_id),
            "active": True,
        },
        {
            "id": "f0f0f0f0-f0f0-f0f0-f0f0-f0f0f0f0f0f0",
            "tenant_id": str(tenant_id),
            "client_id": clients[3]["id"],
            "user_id": str(am2_tenant_user_id),
            "active": True,
        },
    ]
    http.upsert("client_ownership", json_body=ownership, on_conflict="id")

    now = datetime.now(tz=UTC).replace(microsecond=0)
    touches = [
        {
            "id": "10101010-1010-1010-1010-101010101010",
            "tenant_id": str(tenant_id),
            "client_id": clients[0]["id"],
            "scheduled_at": iso(now + timedelta(days=1, hours=2)),
            "stage": "Pre-Meeting Intelligence",
            "lookback_window_days": 30,
        },
        {
            "id": "20202020-2020-2020-2020-202020202020",
            "tenant_id": str(tenant_id),
            "client_id": clients[1]["id"],
            "scheduled_at": iso(now + timedelta(days=2, hours=5)),
            "stage": "Task Approval",
            "lookback_window_days": 30,
        },
        {
            "id": "30303030-3030-3030-3030-303030303030",
            "tenant_id": str(tenant_id),
            "client_id": clients[2]["id"],
            "scheduled_at": iso(now + timedelta(days=3, hours=1)),
            "stage": "QA Audit",
            "lookback_window_days": 30,
        },
    ]
    http.upsert("monthly_touches", json_body=touches, on_conflict="id")

    http.upsert(
        "prompt_templates",
        json_body=[
            {
                "id": "abababab-abab-abab-abab-abababababab",
                "tenant_id": str(tenant_id),
                "category": "Monthly Touch",
                "name": "Monthly Touch Brief Structure",
                "status": "active",
                "provider": "Claude",
                "active_version": "v1",
            },
            {
                "id": "bcbcbcbc-bcbc-bcbc-bcbc-bcbcbcbcbcbc",
                "tenant_id": str(tenant_id),
                "category": "Follow-Up",
                "name": "Ticket Extraction Rules",
                "status": "active",
                "provider": "Gemini",
                "active_version": "v1",
            },
            {
                "id": "cdcdcdcd-cdcd-cdcd-cdcd-cdcdcdcdcdcd",
                "tenant_id": str(tenant_id),
                "category": "Retention",
                "name": "Retention Analysis",
                "status": "draft",
                "provider": "Mixed",
                "active_version": "v1",
            },
        ],
        on_conflict="id",
    )

    run = http.upsert(
        "ownership_sync_runs",
        json_body={
            "id": "99999999-9999-9999-9999-999999999999",
            "tenant_id": str(tenant_id),
            "provider": "ClickUp",
            "source": "Client Health Tracker",
            "cadence_minutes": 15,
            "matched_clients": 112,
            "unmatched_clients": 3,
            "status": "completed",
            "started_at": iso(now - timedelta(minutes=15)),
            "finished_at": iso(now - timedelta(minutes=14)),
        },
        on_conflict="id",
    )
    run_id = run[0]["id"] if run else None

    http.upsert(
        "ownership_sync_exceptions",
        json_body=[
            {
                "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "tenant_id": str(tenant_id),
                "run_id": run_id,
                "client_name": "Harbor Ortho",
                "external_account_manager": "Ari Cole",
                "suggested_user_name": "Ariana Cole",
                "reason": "ClickUp AM label does not exactly match an MTOS user name.",
                "status": "open",
                "last_seen_at": iso(now - timedelta(minutes=14)),
            },
            {
                "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                "tenant_id": str(tenant_id),
                "run_id": run_id,
                "client_name": "Blue Valley Dental",
                "external_account_manager": "Samir Patel",
                "suggested_user_name": None,
                "reason": "No MTOS user matches the ClickUp Account Manager field.",
                "status": "open",
                "last_seen_at": iso(now - timedelta(minutes=14)),
            },
        ],
        on_conflict="id",
    )

    print("Seed complete.")
    print(f"tenant_id={tenant_id}")
    print(f"admin_tenant_user_id={admin_tenant_user_id}")
    print(f"am1_tenant_user_id={am1_tenant_user_id}")
    print(f"am2_tenant_user_id={am2_tenant_user_id}")


if __name__ == "__main__":
    main()

