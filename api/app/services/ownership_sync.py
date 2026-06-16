from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.integrations.clickup import ClickUpClient, ClickUpTask, extract_account_manager_name
from app.supabase_http import SupabaseHTTP


def _normalize_name(value: str) -> str:
    return " ".join(value.lower().strip().split())


def _suggest_user_name(external_name: str, user_full_names: list[str]) -> str | None:
    external_norm = _normalize_name(external_name)
    if not external_norm:
        return None

    # Exact normalized match.
    exact = [name for name in user_full_names if _normalize_name(name) == external_norm]
    if len(exact) == 1:
        return exact[0]

    # Token prefix match (handles "Ari Cole" -> "Ariana Cole").
    external_tokens = external_norm.split()
    candidates: list[str] = []
    for name in user_full_names:
        tokens = _normalize_name(name).split()
        if len(tokens) < len(external_tokens):
            continue
        ok = True
        for ext_token, token in zip(external_tokens, tokens, strict=False):
            if not token.startswith(ext_token):
                ok = False
                break
        if ok:
            candidates.append(name)
    if len(candidates) == 1:
        return candidates[0]
    return None


@dataclass(frozen=True)
class OwnershipSyncConfig:
    clickup_list_id: str
    clickup_am_custom_field_id: str | None = None
    clickup_include_closed: bool = False
    clickup_max_pages: int = 1
    clickup_max_tasks: int = 5


class OwnershipSyncService:
    def __init__(
        self,
        http: SupabaseHTTP,
        clickup: ClickUpClient,
        config: OwnershipSyncConfig,
    ) -> None:
        self._http = http
        self._clickup = clickup
        self._config = config

    def run(self, tenant_id: str) -> dict[str, Any]:
        now = datetime.now(tz=UTC).replace(microsecond=0)
        run_row = self._http.post(
            "ownership_sync_runs",
            json_body={
                "tenant_id": tenant_id,
                "provider": "ClickUp",
                "source": "Client Health Tracker",
                "cadence_minutes": 15,
                "status": "running",
            },
        )
        run_id = (run_row[0].get("id") if run_row else None) or None

        matched = 0
        unmatched = 0
        exception_count = 0

        clients = self._http.get(
            "clients",
            params={"select": "id,name,external_ref", "tenant_id": f"eq.{tenant_id}"},
        )
        clients_by_external_ref = {
            str(row.get("external_ref")): row for row in clients if row.get("external_ref") is not None
        }
        clients_by_name = {_normalize_name(row["name"]): row for row in clients if row.get("name")}

        users = self._http.get(
            "tenant_users",
            params={"select": "id,full_name", "tenant_id": f"eq.{tenant_id}"},
        )
        users_by_norm_name = {_normalize_name(row["full_name"]): row for row in users if row.get("full_name")}
        user_names = [row["full_name"] for row in users if row.get("full_name")]

        active_ownership = self._http.get(
            "client_ownership",
            params={
                "select": "id,client_id,user_id,active",
                "tenant_id": f"eq.{tenant_id}",
                "active": "eq.true",
            },
        )
        ownership_by_client_id = {row["client_id"]: row for row in active_ownership if row.get("client_id")}

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

        for task in tasks:
            client_row = None
            if task.id and task.id in clients_by_external_ref:
                client_row = clients_by_external_ref[task.id]
            elif task.name:
                client_row = clients_by_name.get(_normalize_name(task.name))

            am_name = extract_account_manager_name(task, self._config.clickup_am_custom_field_id) or "Unassigned"
            user_row = users_by_norm_name.get(_normalize_name(am_name)) if am_name else None

            if not client_row:
                unmatched += 1
                exception_count += self._touch_exception(
                    tenant_id=tenant_id,
                    run_id=run_id,
                    client_name=task.name or "Unknown client",
                    external_account_manager=am_name,
                    suggested_user_name=_suggest_user_name(am_name, user_names) if am_name else None,
                    reason="No MTOS client matches the ClickUp task.",
                    now=now,
                )
                continue

            if not user_row:
                unmatched += 1
                exception_count += self._touch_exception(
                    tenant_id=tenant_id,
                    run_id=run_id,
                    client_name=client_row["name"],
                    external_account_manager=am_name,
                    suggested_user_name=_suggest_user_name(am_name, user_names) if am_name else None,
                    reason="No MTOS user matches the ClickUp Account Manager assignment.",
                    now=now,
                )
                continue

            matched += 1
            self._apply_ownership(
                tenant_id=tenant_id,
                client_id=client_row["id"],
                user_id=user_row["id"],
                ownership_by_client_id=ownership_by_client_id,
                now=now,
            )
            self._resolve_open_exceptions(tenant_id=tenant_id, client_name=client_row["name"], now=now)

        if run_id:
            self._http.patch(
                "ownership_sync_runs",
                params={"id": f"eq.{run_id}"},
                json_body={
                    "finished_at": now.isoformat(),
                    "matched_clients": matched,
                    "unmatched_clients": unmatched,
                    "status": "completed",
                },
            )

        return {
            "run_id": run_id,
            "matched_clients": matched,
            "unmatched_clients": unmatched,
            "exception_count": exception_count,
        }

    def _apply_ownership(
        self,
        tenant_id: str,
        client_id: str,
        user_id: str,
        ownership_by_client_id: dict[str, dict[str, Any]],
        now: datetime,
    ) -> None:
        current = ownership_by_client_id.get(client_id)
        if current and current.get("user_id") == user_id:
            self._http.patch(
                "client_ownership",
                params={"id": f"eq.{current['id']}"},
                json_body={"synced_at": now.isoformat()},
            )
            return

        if current and current.get("id"):
            self._http.patch(
                "client_ownership",
                params={"id": f"eq.{current['id']}"},
                json_body={"active": False},
            )

        inserted = self._http.post(
            "client_ownership",
            json_body={
                "tenant_id": tenant_id,
                "client_id": client_id,
                "user_id": user_id,
                "source": "clickup_sync",
                "synced_at": now.isoformat(),
                "active": True,
            },
        )
        if inserted:
            ownership_by_client_id[client_id] = inserted[0]

    def _touch_exception(
        self,
        tenant_id: str,
        run_id: str | None,
        client_name: str,
        external_account_manager: str,
        suggested_user_name: str | None,
        reason: str,
        now: datetime,
    ) -> int:
        existing = self._http.get(
            "ownership_sync_exceptions",
            params={
                "select": "id",
                "tenant_id": f"eq.{tenant_id}",
                "status": "eq.open",
                "client_name": f"eq.{client_name}",
                "external_account_manager": f"eq.{external_account_manager}",
                "reason": f"eq.{reason}",
                "limit": "1",
            },
        )
        if existing:
            self._http.patch(
                "ownership_sync_exceptions",
                params={"id": f"eq.{existing[0]['id']}"},
                json_body={
                    "last_seen_at": now.isoformat(),
                    "run_id": run_id,
                    "suggested_user_name": suggested_user_name,
                },
            )
            return 0

        self._http.post(
            "ownership_sync_exceptions",
            json_body={
                "tenant_id": tenant_id,
                "run_id": run_id,
                "client_name": client_name,
                "external_account_manager": external_account_manager,
                "suggested_user_name": suggested_user_name,
                "reason": reason,
                "status": "open",
                "last_seen_at": now.isoformat(),
            },
        )
        return 1

    def _resolve_open_exceptions(self, tenant_id: str, client_name: str, now: datetime) -> None:
        self._http.patch(
            "ownership_sync_exceptions",
            params={"tenant_id": f"eq.{tenant_id}", "client_name": f"eq.{client_name}", "status": "eq.open"},
            json_body={"status": "resolved", "resolved_at": now.isoformat()},
            prefer="return=minimal",
        )
