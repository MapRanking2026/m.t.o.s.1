from fastapi.testclient import TestClient

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
    assert payload["tenantName"] == "Northstar Growth"
    assert len(payload["clients"]) >= 1


def test_account_manager_only_sees_assigned_clients() -> None:
    response = client.get("/api/v1/clients", headers=account_manager_headers)
    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["owner"] == "Mila Grant"


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
