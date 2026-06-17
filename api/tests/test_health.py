import os

from fastapi.testclient import TestClient

os.environ["MTOS_REPOSITORY_MODE"] = "in_memory"
os.environ["MTOS_TRUST_DEMO_HEADERS"] = "true"

from app.main import app


client = TestClient(app)
account_manager_headers = {"X-MTOS-User-Id": "user_2", "X-MTOS-Role": "account_manager"}
admin_headers = {"X-MTOS-User-Id": "user_1", "X-MTOS-Role": "admin"}


def test_healthcheck() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_overview_shape() -> None:
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 200

    payload = response.json()
    assert payload["tenantName"] == "MTOS Workspace"
    assert len(payload["clients"]) >= 1


def test_account_manager_only_sees_assigned_clients() -> None:
    response = client.get("/api/v1/clients", headers=account_manager_headers)
    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["owner"] == "Mila Grant"


def test_account_manager_can_view_assigned_client_workspace() -> None:
    response = client.get("/api/v1/clients/client_2", headers=account_manager_headers)
    assert response.status_code == 200

    payload = response.json()
    assert payload["client"]["name"] == "Northwind Legal"
    assert payload["client"]["owner"] == "Mila Grant"
    assert payload["visibilityScope"].startswith("Ownership filtering")


def test_account_manager_cannot_view_unassigned_client_workspace() -> None:
    response = client.get("/api/v1/clients/client_1", headers=account_manager_headers)
    assert response.status_code == 404


def test_account_manager_can_sync_visible_client_intelligence() -> None:
    response = client.post("/api/v1/clients/client_2/intelligence/sync", headers=account_manager_headers)
    assert response.status_code == 200

    payload = response.json()
    assert payload["source"] == "ClickUp"
    assert payload["syncedAt"]


def test_clickup_status_includes_connection_and_cursor_state() -> None:
    sync_response = client.post("/api/v1/ownership/sync", headers=admin_headers)
    assert sync_response.status_code == 200

    intelligence_response = client.post("/api/v1/clients/client_2/intelligence/sync", headers=account_manager_headers)
    assert intelligence_response.status_code == 200

    response = client.get("/api/v1/integrations/clickup/status", headers=admin_headers)
    assert response.status_code == 200

    payload = response.json()
    assert payload["configured"] is True
    assert payload["connection"]["health"] == "connected"
    assert payload["ownershipCursor"]["status"] == "completed"
    assert payload["intelligenceCursor"]["status"] == "completed"


def test_ownership_exceptions_require_admin_access() -> None:
    forbidden = client.get("/api/v1/ownership/exceptions", headers=account_manager_headers)
    assert forbidden.status_code == 403

    allowed = client.get("/api/v1/ownership/exceptions", headers=admin_headers)
    assert allowed.status_code == 200
    assert len(allowed.json()) >= 1


def test_ownership_sync_returns_summary() -> None:
    response = client.post("/api/v1/ownership/sync", headers=admin_headers)
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["summary"]["provider"] == "ClickUp"
