import type {
  ClientIntelligenceSnapshot,
  ClientRecord,
  ClientWorkspace,
  ClickUpIntegrationStatus,
  ClickUpClientImportResult,
  DashboardOverview,
  MonthlyTouchDetail,
  MonthlyTouchRecord,
  OwnershipExceptionRecord,
  OwnershipSyncRunResult,
  OwnershipSyncSummary,
  PromptTemplateDetail,
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

export function fetchMonthlyTouchDetail(touchId: string) {
  return requestJson<MonthlyTouchDetail>(`/api/v1/monthly-touches/${touchId}`);
}

export function fetchPromptTemplates() {
  return requestJson<PromptTemplateRecord[]>("/api/v1/prompts");
}

export function fetchPromptDetail(promptId: string) {
  return requestJson<PromptTemplateDetail>(`/api/v1/prompts/${promptId}`);
}

export function createPromptVersion(promptId: string, payload: { systemPrompt: string; userPrompt: string }) {
  return requestJson<PromptTemplateDetail>(`/api/v1/prompts/${promptId}/versions`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function activatePromptVersion(promptId: string, versionId: string) {
  return requestJson<PromptTemplateDetail>(`/api/v1/prompts/${promptId}/activate`, {
    method: "POST",
    body: JSON.stringify({ versionId }),
  });
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

export function importClickUpClients() {
  return requestJson<ClickUpClientImportResult>("/api/v1/integrations/clickup/import-clients", {
    method: "POST",
  });
}

export function fetchRuntimeStatus() {
  return requestJson<RuntimeStatus>("/api/v1/runtime-status");
}
