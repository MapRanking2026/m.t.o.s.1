export type HealthTrend = "up" | "down" | "stable";

export interface UserProfile {
  id: string;
  fullName: string;
  role: "admin" | "account_manager";
  email: string;
}

export interface MetricCard {
  id: string;
  label: string;
  value: string;
  detail: string;
  trend: HealthTrend;
}

export interface ClientRecord {
  id: string;
  name: string;
  owner: string;
  healthScore: number;
  riskLevel: "Low" | "Medium" | "High";
  nextTouchAt: string;
  topOpportunity: string;
}

export interface MonthlyTouchRecord {
  id: string;
  clientName: string;
  scheduledAt: string;
  stage:
    | "Pre-Meeting Intelligence"
    | "Meeting Scheduled"
    | "Meeting Intelligence"
    | "Task Approval"
    | "Recap Approval"
    | "QA Audit";
  owner: string;
}

export interface PromptTemplateRecord {
  id: string;
  name: string;
  category: string;
  version: string;
  status: "Active" | "Draft" | "Archived";
  provider: "Claude" | "Gemini" | "Mixed";
}

export interface ActivityRecord {
  id: string;
  title: string;
  description: string;
  at: string;
  kind: "brief" | "sync" | "risk" | "qa" | "recap";
}

export interface DashboardOverview {
  tenantName: string;
  currentUser: UserProfile;
  metrics: MetricCard[];
  clients: ClientRecord[];
  monthlyTouches: MonthlyTouchRecord[];
  promptTemplates: PromptTemplateRecord[];
  activity: ActivityRecord[];
}

export interface OwnershipExceptionRecord {
  id: string;
  clientName: string;
  externalAccountManager: string;
  suggestedUserName: string | null;
  reason: string;
  status: "open" | "resolved";
  lastSeenAt: string;
}

export interface OwnershipSyncSummary {
  provider: string;
  source: string;
  cadenceMinutes: number;
  lastRunAt: string;
  matchedClients: number;
  unmatchedClients: number;
  exceptionCount: number;
}

export interface OwnershipSyncRunResult {
  status: "completed";
  summary: OwnershipSyncSummary;
  exceptions: OwnershipExceptionRecord[];
}

export interface DemoIdentity {
  id: string;
  fullName: string;
  role: UserProfile["role"];
  tenantUserId?: string | null;
}
