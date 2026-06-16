import { useQuery } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/layout/app-shell";
import { fetchDashboardOverview } from "@/lib/api";
import ClientsPage from "@/pages/ClientsPage";
import DashboardPage from "@/pages/DashboardPage";
import MonthlyTouchesPage from "@/pages/MonthlyTouchesPage";
import PromptCenterPage from "@/pages/PromptCenterPage";
import SettingsPage from "@/pages/SettingsPage";

export default function App() {
  const { data } = useQuery({
    queryKey: ["shell-overview"],
    queryFn: fetchDashboardOverview,
  });

  if (!data) {
    return <div className="min-h-screen animate-pulse bg-background" />;
  }

  return (
    <BrowserRouter>
      <AppShell currentUser={data.currentUser} tenantName={data.tenantName}>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/clients" element={<ClientsPage />} />
          <Route path="/monthly-touches" element={<MonthlyTouchesPage />} />
          <Route path="/prompts" element={<PromptCenterPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}
