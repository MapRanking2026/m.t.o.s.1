import type {
  ClientIntelligenceSnapshot,
  ClientRecord,
  ClientWorkspace,
  ClickUpIntegrationStatus,
  DashboardOverview,
  MonthlyTouchRecord,
  OwnershipExceptionRecord,
  OwnershipSyncRunResult,
  OwnershipSyncSummary,
  PromptTemplateRecord,
  RuntimeStatus,
} from "@/types/mtos";
import { useAppStore } from "@/store/app-store";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "";
  const state = useAppStore.getState();
  const accessToken = state.accessToken;
  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    let detail = "";
    try {
      const payload = (await response.json()) as unknown;
      if (payload && typeof payload === "object" && "detail" in payload && typeof payload.detail === "string") {
        detail = payload.detail;
      }
    } catch {
      detail = "";
    }
    throw new Error(detail ? `${detail}` : `Request failed for ${path}`);
  }

  return (await response.json()) as T;
}

export function fetchDashboardOverview() {
  return requestJson<DashboardOverview>("/api/v1/dashboard/overview");
}

export function fetchClients() {
  return requestJson<ClientRecord[]>("/api/v1/clients");
}

export function fetchClientWorkspace(clientId: string) {
  return requestJson<ClientWorkspace>(`/api/v1/clients/${clientId}`);
}

export function syncClientIntelligence(clientId: string) {
  return requestJson<ClientIntelligenceSnapshot>(`/api/v1/clients/${clientId}/intelligence/sync`, {
    method: "POST",
  });
}

export function fetchMonthlyTouches() {
  return requestJson<MonthlyTouchRecord[]>("/api/v1/monthly-touches");
}

export function fetchPromptTemplates() {
  return requestJson<PromptTemplateRecord[]>("/api/v1/prompts");
}

export function fetchOwnershipSyncSummary() {
  return requestJson<OwnershipSyncSummary>("/api/v1/ownership/summary");
}

export function fetchOwnershipExceptions() {
  return requestJson<OwnershipExceptionRecord[]>("/api/v1/ownership/exceptions");
}

export function runOwnershipSync() {
  return requestJson<OwnershipSyncRunResult>("/api/v1/ownership/sync", {
    method: "POST",
  });
}

export function fetchClickUpIntegrationStatus() {
  return requestJson<ClickUpIntegrationStatus>("/api/v1/integrations/clickup/status");
}

export function fetchRuntimeStatus() {
  return requestJson<RuntimeStatus>("/api/v1/runtime-status");
}
