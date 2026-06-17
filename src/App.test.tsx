import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/supabase", () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({
        data: {
          session: {
            access_token: "test-token",
            user: { id: "auth_user_1" },
          },
        },
      }),
      onAuthStateChange: vi.fn().mockReturnValue({
        data: { subscription: { unsubscribe: vi.fn() } },
      }),
      signOut: vi.fn().mockResolvedValue({ error: null }),
      signInWithPassword: vi.fn().mockResolvedValue({ error: null }),
      signInWithOAuth: vi.fn().mockResolvedValue({ error: null }),
      resetPasswordForEmail: vi.fn().mockResolvedValue({ error: null }),
    },
  },
}));

import App from "@/App";
import { AuthProvider } from "@/app/auth-provider";

const dashboardOverview = {
  tenantName: "MTOS Workspace",
  currentUser: {
    id: "user_1",
    fullName: "Ariana Cole",
    role: "admin",
    email: "ariana@northstargrowth.com",
  },
  metrics: [
    { id: "1", label: "Briefs Ready", value: "18", detail: "4 due in 24h", trend: "up" },
    { id: "2", label: "Retention Risks", value: "6", detail: "2 escalated", trend: "down" },
    { id: "3", label: "Pending Approvals", value: "14", detail: "Tasks + recaps", trend: "stable" },
    { id: "4", label: "QA Coverage", value: "92%", detail: "Last 30 days", trend: "up" },
  ],
  clients: [
    {
      id: "client_1",
      name: "BluePeak Dental",
      owner: "Ariana Cole",
      healthScore: 84,
      riskLevel: "Low",
      nextTouchAt: "Jun 18 · 11:00 AM",
      topOpportunity: "GBP optimization",
    },
  ],
  monthlyTouches: [
    {
      id: "touch_1",
      clientName: "BluePeak Dental",
      scheduledAt: "Jun 18 · 11:00 AM",
      stage: "Pre-Meeting Intelligence",
      owner: "Ariana Cole",
    },
  ],
  promptTemplates: [
    {
      id: "prompt_1",
      name: "Monthly Touch Brief Structure",
      category: "Briefs",
      version: "v12",
      status: "Active",
      provider: "Claude",
    },
  ],
  activity: [
    {
      id: "act_1",
      title: "Brief generated",
      description: "BluePeak Dental brief completed with 30 day context.",
      at: "2m ago",
      kind: "brief",
    },
  ],
};

vi.stubGlobal(
  "fetch",
  vi.fn().mockResolvedValue({
    ok: true,
    json: async () => dashboardOverview,
  }),
);

describe("App", () => {
  it("renders the MTOS command center shell", async () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </QueryClientProvider>,
    );

    expect(await screen.findByText("MTOS Command Center")).toBeInTheDocument();
    expect(screen.getByText("Monthly Touch")).toBeInTheDocument();
  });
});
