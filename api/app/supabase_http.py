from __future__ import annotations

from typing import Any

import httpx


class SupabaseHTTP:
    def __init__(self, supabase_url: str, apikey: str, auth_bearer: str | None = None) -> None:
        self._base_url = supabase_url.rstrip("/")
        self._apikey = apikey
        self._auth_bearer = auth_bearer

    def get(self, table: str, params: dict[str, str]) -> list[dict[str, Any]]:
        with self._client() as client:
            response = client.get(self._table_url(table), params=params)
            response.raise_for_status()
            payload = response.json()
        if isinstance(payload, list):
            return payload
        return []

    def post(
        self,
        table: str,
        json_body: Any,
        prefer: str = "return=representation",
        params: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        with self._client(prefer=prefer) as client:
            response = client.post(self._table_url(table), json=json_body, params=params)
            response.raise_for_status()
            payload = response.json()
        if isinstance(payload, list):
            return payload
        return []

    def upsert(
        self,
        table: str,
        json_body: Any,
        on_conflict: str | None = None,
        prefer: str = "resolution=merge-duplicates,return=representation",
    ) -> list[dict[str, Any]]:
        params: dict[str, str] | None = None
        if on_conflict:
            params = {"on_conflict": on_conflict}
        return self.post(table=table, json_body=json_body, prefer=prefer, params=params)

    def patch(
        self,
        table: str,
        params: dict[str, str],
        json_body: Any,
        prefer: str = "return=representation",
    ) -> list[dict[str, Any]]:
        with self._client(prefer=prefer) as client:
            response = client.patch(self._table_url(table), params=params, json=json_body)
            response.raise_for_status()
            payload = response.json()
        if isinstance(payload, list):
            return payload
        return []

    def _client(self, prefer: str | None = None) -> httpx.Client:
        headers = {
            "apikey": self._apikey,
        }
        if self._auth_bearer:
            headers["Authorization"] = f"Bearer {self._auth_bearer}"
        else:
            headers["Authorization"] = f"Bearer {self._apikey}"
        if prefer:
            headers["Prefer"] = prefer

        return httpx.Client(headers=headers, timeout=10.0)

    def _table_url(self, table: str) -> str:
        return f"{self._base_url}/rest/v1/{table}"

