from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import HTTPException, status


@dataclass(frozen=True)
class ClickUpTask:
    id: str
    name: str
    assignees: list[dict[str, Any]]
    custom_fields: list[dict[str, Any]]
    status: dict[str, Any] | None
    priority: dict[str, Any] | None
    due_date: str | None
    date_updated: str | None
    url: str | None

    @staticmethod
    def from_api(payload: dict[str, Any]) -> "ClickUpTask":
        return ClickUpTask(
            id=str(payload.get("id") or ""),
            name=str(payload.get("name") or ""),
            assignees=list(payload.get("assignees") or []),
            custom_fields=list(payload.get("custom_fields") or []),
            status=payload.get("status") if isinstance(payload.get("status"), dict) else None,
            priority=payload.get("priority") if isinstance(payload.get("priority"), dict) else None,
            due_date=str(payload.get("due_date")) if payload.get("due_date") is not None else None,
            date_updated=str(payload.get("date_updated")) if payload.get("date_updated") is not None else None,
            url=str(payload.get("url")) if payload.get("url") is not None else None,
        )


class ClickUpClient:
    def __init__(
        self,
        api_token: str,
        base_url: str = "https://api.clickup.com/api/v2",
        timeout_seconds: float = 15.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._api_token = api_token
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._http_client = http_client

    def list_tasks(self, list_id: str, page: int = 0, include_closed: bool = False) -> list[ClickUpTask]:
        params = {
            "page": str(page),
            "include_closed": "true" if include_closed else "false",
            "subtasks": "false",
        }
        payload = self._get(f"/list/{list_id}/task", params=params)
        tasks = payload.get("tasks") if isinstance(payload, dict) else None
        if not isinstance(tasks, list):
            return []
        return [ClickUpTask.from_api(item) for item in tasks if isinstance(item, dict)]

    def ping(self) -> None:
        # Cheap endpoint to verify token validity.
        self._get("/user")

    def _get(self, path: str, params: dict[str, str] | None = None) -> Any:
        url = f"{self._base_url}{path}"
        if self._http_client is not None:
            response = self._http_client.get(url, params=params)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = exc.response.text.strip() if exc.response is not None else str(exc)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"ClickUp request failed: {detail[:500]}",
                ) from exc
            return response.json()

        with httpx.Client(
            headers={"Authorization": self._api_token},
            timeout=self._timeout_seconds,
        ) as client:
            response = client.get(url, params=params)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = exc.response.text.strip() if exc.response is not None else str(exc)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"ClickUp request failed: {detail[:500]}",
                ) from exc
            return response.json()


def extract_account_manager_name(task: ClickUpTask, am_custom_field_id: str | None = None) -> str | None:
    if am_custom_field_id:
        for field in task.custom_fields:
            if str(field.get("id") or "") != am_custom_field_id:
                continue
            value = field.get("value")
            if value is None:
                return None
            if isinstance(value, str):
                return value.strip() or None
            if isinstance(value, dict):
                for key in ("full_name", "name", "username", "label"):
                    candidate = value.get(key)
                    if isinstance(candidate, str) and candidate.strip():
                        return candidate.strip()
            if isinstance(value, int):
                type_config = field.get("type_config") or {}
                options = type_config.get("options")
                if isinstance(options, list):
                    for option in options:
                        if isinstance(option, dict) and option.get("id") == value:
                            name = option.get("name")
                            if isinstance(name, str) and name.strip():
                                return name.strip()
            return str(value).strip() or None

    if task.assignees:
        first = task.assignees[0]
        for key in ("full_name", "username", "email"):
            value = first.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None
