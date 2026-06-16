import type {
  ClientRecord,
  DashboardOverview,
  MonthlyTouchRecord,
  OwnershipExceptionRecord,
  OwnershipSyncRunResult,
  OwnershipSyncSummary,
  PromptTemplateRecord,
} from "@/types/mtos";
import { useAppStore } from "@/store/app-store";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "";
  const actingIdentity = useAppStore.getState().actingIdentity;
  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-MTOS-User-Id": actingIdentity.id,
      "X-MTOS-Role": actingIdentity.role,
      ...(actingIdentity.tenantUserId ? { "X-MTOS-Tenant-User-Id": actingIdentity.tenantUserId } : {}),
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed for ${path}`);
  }

  return (await response.json()) as T;
}

export function fetchDashboardOverview() {
  return requestJson<DashboardOverview>("/api/v1/dashboard/overview");
}

export function fetchClients() {
  return requestJson<ClientRecord[]>("/api/v1/clients");
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
