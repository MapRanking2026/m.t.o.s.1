from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.integrations.clickup import ClickUpTask
from app.services.client_intelligence_sync import ClientIntelligenceSyncConfig, ClientIntelligenceSyncService


@dataclass
class FakeSupabaseHTTP:
    tables: dict[str, list[dict[str, Any]]]

    def upsert(
        self,
        table: str,
        json_body: dict[str, Any],
        on_conflict: str | None = None,
        prefer: str = "resolution=merge-duplicates,return=representation",
    ) -> list[dict[str, Any]]:
        rows = self.tables.setdefault(table, [])
        keys = [item.strip() for item in (on_conflict or "").split(",") if item.strip()]
        for index, row in enumerate(rows):
            if keys and all(str(row.get(key)) == str(json_body.get(key)) for key in keys):
                updated = row.copy()
                updated.update(json_body)
                updated.setdefault("id", row.get("id") or str(uuid4()))
                rows[index] = updated
                return [updated.copy()]

        inserted = json_body.copy()
        inserted.setdefault("id", str(uuid4()))
        rows.append(inserted)
        return [inserted.copy()]


class FakeClickUp:
    def __init__(self, tasks: list[ClickUpTask]) -> None:
        self._tasks = tasks

    def list_tasks(self, list_id: str, page: int = 0, include_closed: bool = False) -> list[ClickUpTask]:
        return self._tasks if page == 0 else []


def test_client_intelligence_sync_persists_connected_snapshot() -> None:
    tenant_id = "11111111-1111-1111-1111-111111111111"
    http = FakeSupabaseHTTP(tables={"client_intelligence_snapshots": []})
    service = ClientIntelligenceSyncService(
        http=http,  # type: ignore[arg-type]
        clickup=FakeClickUp(
            [
                ClickUpTask(
                    id="task_1",
                    name="BluePeak Dental",
                    assignees=[{"full_name": "Ariana Cole"}],
                    custom_fields=[{"id": "health", "name": "Client health", "value": 84}],
                    status={"status": "on track"},
                    priority={"priority": "high"},
                    due_date="1781606400000",
                    date_updated="1781520000000",
                    url="https://app.clickup.com/t/task_1",
                )
            ]
        ),  # type: ignore[arg-type]
        config=ClientIntelligenceSyncConfig(clickup_list_id="list_1"),
    )

    snapshot = service.sync_client(
        tenant_id=tenant_id,
        client_row={"id": "client_1", "name": "BluePeak Dental", "external_ref": "task_1"},
    )

    assert snapshot.sync_status == "connected"
    assert snapshot.clickup_task_id == "task_1"
    assert snapshot.account_manager == "Ariana Cole"
    assert "Tracker status: on track" in snapshot.signals
    assert len(http.tables["client_intelligence_snapshots"]) == 1


def test_client_intelligence_sync_persists_not_found_snapshot_when_no_clickup_match() -> None:
    tenant_id = "11111111-1111-1111-1111-111111111111"
    http = FakeSupabaseHTTP(tables={"client_intelligence_snapshots": []})
    service = ClientIntelligenceSyncService(
        http=http,  # type: ignore[arg-type]
        clickup=FakeClickUp([]),  # type: ignore[arg-type]
        config=ClientIntelligenceSyncConfig(clickup_list_id="list_1"),
    )

    snapshot = service.sync_client(
        tenant_id=tenant_id,
        client_row={"id": "client_1", "name": "BluePeak Dental", "external_ref": "task_1"},
    )

    assert snapshot.sync_status == "not_found"
    assert snapshot.clickup_task_id is None
    assert "Verify the MTOS client external_ref matches the ClickUp task ID." in snapshot.signals
