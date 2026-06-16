import type { PropsWithChildren } from "react";

import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import type { UserProfile } from "@/types/mtos";

interface AppShellProps extends PropsWithChildren {
  tenantName: string;
  currentUser: UserProfile;
}

export function AppShell({ children, tenantName, currentUser }: AppShellProps) {
  return (
    <div className="min-h-screen bg-background px-4 py-4 text-foreground lg:px-6">
      <div className="mx-auto grid min-h-[calc(100vh-2rem)] max-w-[1700px] gap-4 lg:grid-cols-[300px_minmax(0,1fr)]">
        <div className="lg:sticky lg:top-4 lg:h-[calc(100vh-2rem)]">
          <Sidebar />
        </div>
        <main className="space-y-4">
          <Topbar tenantName={tenantName} currentUser={currentUser} />
          {children}
        </main>
      </div>
    </div>
  );
}
