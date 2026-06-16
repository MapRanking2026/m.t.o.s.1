from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import pytest

from app.integrations.clickup import ClickUpTask
from app.services.ownership_sync import OwnershipSyncConfig, OwnershipSyncService


def _apply_filters(rows: list[dict[str, Any]], params: dict[str, str]) -> list[dict[str, Any]]:
    filtered = rows
    for key, raw in params.items():
        if key in {"select", "order", "limit"}:
            continue
        if raw == "is.null":
            filtered = [row for row in filtered if row.get(key) is None]
            continue
        if raw.startswith("eq."):
            value = raw[3:]
            def _eq(row_value: Any) -> bool:
                if isinstance(row_value, bool):
                    return ("true" if row_value else "false") == value.lower()
                return str(row_value) == value

            filtered = [row for row in filtered if _eq(row.get(key))]
            continue
    limit = params.get("limit")
    if limit and limit.isdigit():
        return filtered[: int(limit)]
    return filtered


@dataclass
class FakeSupabaseHTTP:
    tables: dict[str, list[dict[str, Any]]]

    def get(self, table: str, params: dict[str, str]) -> list[dict[str, Any]]:
        return [row.copy() for row in _apply_filters(self.tables.get(table, []), params)]

    def post(
        self,
        table: str,
        json_body: Any,
        prefer: str = "return=representation",
        params: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        if isinstance(json_body, dict):
            rows = [json_body]
        else:
            rows = list(json_body)
        for row in rows:
            row.setdefault("id", str(uuid4()))
            self.tables.setdefault(table, []).append(row.copy())
        return [row.copy() for row in rows] if "return=minimal" not in (prefer or "") else []

    def patch(
        self,
        table: str,
        params: dict[str, str],
        json_body: Any,
        prefer: str = "return=representation",
    ) -> list[dict[str, Any]]:
        updated: list[dict[str, Any]] = []
        for row in self.tables.get(table, []):
            if row in _apply_filters([row], params):
                row.update(json_body)
                updated.append(row.copy())
        return updated if "return=minimal" not in (prefer or "") else []


class FakeClickUp:
    def __init__(self, tasks: list[ClickUpTask]) -> None:
        self._tasks = tasks

    def list_tasks(self, list_id: str, page: int = 0, include_closed: bool = False) -> list[ClickUpTask]:
        return self._tasks if page == 0 else []


def test_ownership_sync_updates_active_ownership_and_creates_exception() -> None:
    tenant_id = "11111111-1111-1111-1111-111111111111"
    http = FakeSupabaseHTTP(
        tables={
            "clients": [
                {"id": "client_1", "tenant_id": tenant_id, "name": "BluePeak Dental", "external_ref": "task_1"},
            ],
            "tenant_users": [
                {"id": "tu_1", "tenant_id": tenant_id, "full_name": "Ariana Cole"},
                {"id": "tu_2", "tenant_id": tenant_id, "full_name": "Mila Grant"},
            ],
            "client_ownership": [
                {
                    "id": "own_1",
                    "tenant_id": tenant_id,
                    "client_id": "client_1",
                    "user_id": "tu_1",
                    "active": True,
                }
            ],
            "ownership_sync_runs": [],
            "ownership_sync_exceptions": [],
        }
    )

    tasks = [
        ClickUpTask(
            id="task_1",
            name="BluePeak Dental",
            assignees=[{"full_name": "Mila Grant"}],
            custom_fields=[],
            status=None,
            priority=None,
            due_date=None,
            date_updated=None,
            url=None,
        ),
        ClickUpTask(
            id="task_missing",
            name="Unknown Co",
            assignees=[{"full_name": "Ariana Cole"}],
            custom_fields=[],
            status=None,
            priority=None,
            due_date=None,
            date_updated=None,
            url=None,
        ),
    ]
    sync = OwnershipSyncService(
        http=http,  # type: ignore[arg-type]
        clickup=FakeClickUp(tasks),  # type: ignore[arg-type]
        config=OwnershipSyncConfig(clickup_list_id="list_1"),
    )

    result = sync.run(tenant_id=tenant_id)

    assert result["matched_clients"] == 1
    assert result["unmatched_clients"] == 1
    assert len(http.tables["ownership_sync_runs"]) == 1
    assert http.tables["ownership_sync_runs"][0]["status"] == "completed"

    # Old ownership deactivated, new ownership inserted as active.
    ownership_rows = http.tables["client_ownership"]
    assert any(row["id"] == "own_1" and row["active"] is False for row in ownership_rows)
    assert any(row["client_id"] == "client_1" and row["user_id"] == "tu_2" and row["active"] is True for row in ownership_rows)

    # Exception created for unknown client.
    assert len(http.tables["ownership_sync_exceptions"]) == 1
    exc = http.tables["ownership_sync_exceptions"][0]
    assert exc["client_name"] == "Unknown Co"
    assert exc["status"] == "open"
