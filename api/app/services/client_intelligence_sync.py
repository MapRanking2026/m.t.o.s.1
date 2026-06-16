from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.integrations.clickup import ClickUpClient, ClickUpTask, extract_account_manager_name
from app.models import ClientIntelligenceSnapshot
from app.supabase_http import SupabaseHTTP


def _normalize_name(value: str) -> str:
    return " ".join(value.lower().strip().split())


def _parse_clickup_timestamp(raw_value: str | None) -> str | None:
    if not raw_value:
        return None
    try:
        timestamp = int(raw_value) / 1000
        return datetime.fromtimestamp(timestamp, tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except (TypeError, ValueError, OverflowError):
        return None


def _render_custom_field_value(field: dict[str, Any]) -> str | None:
    value = field.get("value")
    if value in (None, "", []):
        return None
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, float)):
        type_config = field.get("type_config") or {}
        options = type_config.get("options")
        if isinstance(options, list):
            for option in options:
                if isinstance(option, dict) and option.get("id") == value:
                    option_name = option.get("name")
                    if isinstance(option_name, str) and option_name.strip():
                        return option_name.strip()
        return str(value)
    if isinstance(value, dict):
        for key in ("name", "label", "username", "email", "value"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
    if isinstance(value, list):
        rendered = []
        for item in value:
            if isinstance(item, dict):
                label = item.get("name") or item.get("label")
                if isinstance(label, str) and label.strip():
                    rendered.append(label.strip())
            elif isinstance(item, str) and item.strip():
                rendered.append(item.strip())
        if rendered:
            return ", ".join(rendered[:3])
    return str(value).strip() or None


def _build_signals(task: ClickUpTask, account_manager: str | None) -> list[str]:
    signals: list[str] = []
    if account_manager:
        signals.append(f"Account Manager: {account_manager}")

    status_name = task.status.get("status") if task.status else None
    if isinstance(status_name, str) and status_name.strip():
        signals.append(f"Tracker status: {status_name.strip()}")

    priority_name = task.priority.get("priority") if task.priority else None
    if isinstance(priority_name, str) and priority_name.strip():
        signals.append(f"Priority: {priority_name.strip().title()}")

    for field in task.custom_fields:
        name = field.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        rendered_value = _render_custom_field_value(field)
        if not rendered_value:
            continue
        signals.append(f"{name.strip()}: {rendered_value}")
        if len(signals) >= 4:
            break

    return signals[:4]


@dataclass(frozen=True)
class ClientIntelligenceSyncConfig:
    clickup_list_id: str
    clickup_am_custom_field_id: str | None = None
    clickup_include_closed: bool = False
    clickup_max_pages: int = 1
    clickup_max_tasks: int = 10


class ClientIntelligenceSyncService:
    def __init__(self, http: SupabaseHTTP, clickup: ClickUpClient, config: ClientIntelligenceSyncConfig) -> None:
        self._http = http
        self._clickup = clickup
        self._config = config

    def sync_client(self, tenant_id: str, client_row: dict[str, Any]) -> ClientIntelligenceSnapshot:
        task = self._find_matching_task(client_row)
        synced_at = datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

        if task is None:
            payload = {
                "tenant_id": tenant_id,
                "client_id": client_row["id"],
                "source": "clickup",
                "sync_status": "not_found",
                "summary": (
                    "No ClickUp Client Health Tracker task matched this MTOS client by external_ref "
                    "or normalized client name."
                ),
                "signals_json": [
                    "Verify the MTOS client external_ref matches the ClickUp task ID.",
                    "If name fallback is required, keep the ClickUp tracker task name aligned with the MTOS client name.",
                ],
                "synced_at": synced_at,
            }
        else:
            account_manager = extract_account_manager_name(task, self._config.clickup_am_custom_field_id)
            task_status = task.status.get("status") if task.status else None
            task_priority = task.priority.get("priority") if task.priority else None
            due_at = _parse_clickup_timestamp(task.due_date)
            last_activity_at = _parse_clickup_timestamp(task.date_updated)
            sync_status = "connected" if account_manager else "warning"

            summary_bits = [
                f"Matched ClickUp tracker row '{task.name}'.",
                f"Status: {task_status}." if isinstance(task_status, str) and task_status.strip() else None,
                f"Priority: {task_priority}." if isinstance(task_priority, str) and task_priority.strip() else None,
                f"Account manager: {account_manager}." if account_manager else "Account manager is missing from the tracker row.",
            ]

            payload = {
                "tenant_id": tenant_id,
                "client_id": client_row["id"],
                "source": "clickup",
                "sync_status": sync_status,
                "clickup_task_id": task.id or None,
                "clickup_task_name": task.name or None,
                "clickup_task_url": task.url,
                "account_manager": account_manager,
                "task_status": task_status if isinstance(task_status, str) else None,
                "task_priority": task_priority if isinstance(task_priority, str) else None,
                "due_at": due_at,
                "last_activity_at": last_activity_at,
                "summary": " ".join(part for part in summary_bits if part),
                "signals_json": _build_signals(task, account_manager),
                "synced_at": synced_at,
            }

        try:
            rows = self._http.upsert(
                "client_intelligence_snapshots",
                json_body=payload,
                on_conflict="tenant_id,client_id,source",
            )
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text if exc.response is not None else str(exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Client intelligence snapshots are not ready in Supabase. "
                    "Apply migration `202606160001_client_intelligence_snapshots.sql` and retry. "
                    f"Underlying error: {detail[:300]}"
                ),
            ) from exc
        row = rows[0] if rows else payload
        return self._to_snapshot(row)

    def _find_matching_task(self, client_row: dict[str, Any]) -> ClickUpTask | None:
        client_name = str(client_row.get("name") or "")
        external_ref = str(client_row.get("external_ref") or "")

        tasks: list[ClickUpTask] = []
        for page in range(self._config.clickup_max_pages):
            page_tasks = self._clickup.list_tasks(
                list_id=self._config.clickup_list_id,
                page=page,
                include_closed=self._config.clickup_include_closed,
            )
            if not page_tasks:
                break
            tasks.extend(page_tasks)
            if len(tasks) >= self._config.clickup_max_tasks:
                tasks = tasks[: self._config.clickup_max_tasks]
                break

        if external_ref:
            for task in tasks:
                if task.id == external_ref:
                    return task

        normalized_name = _normalize_name(client_name)
        for task in tasks:
            if _normalize_name(task.name) == normalized_name:
                return task
        return None

    @staticmethod
    def _to_snapshot(row: dict[str, Any]) -> ClientIntelligenceSnapshot:
        return ClientIntelligenceSnapshot(
            id=str(row.get("id") or "pending"),
            source=str(row.get("source") or "clickup").title(),
            synced_at=str(row.get("synced_at") or ""),
            sync_status=str(row.get("sync_status") or "not_found"),
            clickup_task_id=str(row.get("clickup_task_id")) if row.get("clickup_task_id") else None,
            clickup_task_name=str(row.get("clickup_task_name")) if row.get("clickup_task_name") else None,
            clickup_task_url=str(row.get("clickup_task_url")) if row.get("clickup_task_url") else None,
            account_manager=str(row.get("account_manager")) if row.get("account_manager") else None,
            task_status=str(row.get("task_status")) if row.get("task_status") else None,
            task_priority=str(row.get("task_priority")).title() if row.get("task_priority") else None,
            due_at=str(row.get("due_at")) if row.get("due_at") else None,
            last_activity_at=str(row.get("last_activity_at")) if row.get("last_activity_at") else None,
            summary=str(row.get("summary") or ""),
            signals=[str(item) for item in list(row.get("signals_json") or []) if str(item).strip()],
        )
