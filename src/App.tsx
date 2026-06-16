import { useQuery } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/layout/app-shell";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { fetchDashboardOverview } from "@/lib/api";
import ClientWorkspacePage from "@/pages/ClientWorkspacePage";
import ClientsPage from "@/pages/ClientsPage";
import DashboardPage from "@/pages/DashboardPage";
import LoginPage from "@/pages/LoginPage";
import MonthlyTouchesPage from "@/pages/MonthlyTouchesPage";
import PromptCenterPage from "@/pages/PromptCenterPage";
import SettingsPage from "@/pages/SettingsPage";

function AuthenticatedApp() {
  const { data } = useQuery({
    queryKey: ["shell-overview"],
    queryFn: fetchDashboardOverview,
  });

  if (!data) {
    return <div className="min-h-screen animate-pulse bg-background" />;
  }

  return (
    <AppShell currentUser={data.currentUser} tenantName={data.tenantName}>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/clients" element={<ClientsPage />} />
        <Route path="/clients/:clientId" element={<ClientWorkspacePage />} />
        <Route path="/monthly-touches" element={<MonthlyTouchesPage />} />
        <Route path="/prompts" element={<PromptCenterPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </AppShell>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <AuthenticatedApp />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
