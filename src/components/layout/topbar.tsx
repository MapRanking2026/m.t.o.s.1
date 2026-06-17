import { useQueryClient } from "@tanstack/react-query";
﻿import { Bell, LogOut, Search, ShieldCheck } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import type { UserProfile } from "@/types/mtos";
import { supabase } from "@/lib/supabase";

interface TopbarProps {
  tenantName: string;
  currentUser: UserProfile;
}

export function Topbar({ tenantName, currentUser }: TopbarProps) {
  const queryClient = useQueryClient();

  const handleLogout = async () => {
    await supabase.auth.signOut();
    void queryClient.invalidateQueries();
  };

  return (
    <header className="flex flex-col gap-4 rounded-[32px] border border-white/10 bg-white/[0.03] p-6 backdrop-blur-xl lg:flex-row lg:items-center lg:justify-between">
      <div>
        <Badge>Enterprise Preview</Badge>
        <h1 className="mt-4 font-display text-4xl tracking-tight text-white">MTOS Command Center</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          Every Monthly Touch, approval gate, and client signal is unified into one operator workflow.
        </p>
      </div>

      <div className="flex flex-col gap-3 lg:items-end">
        <div className="flex items-center justify-end">
          <button
            className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-muted-foreground transition hover:text-white"
            onClick={handleLogout}
            type="button"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-muted-foreground">
            <Search className="h-4 w-4" />
            <span>Search clients, briefs, prompts</span>
          </div>
          <button className="rounded-full border border-white/10 bg-white/5 p-3 text-muted-foreground transition hover:text-white">
            <Bell className="h-4 w-4" />
          </button>
        </div>
        <div className="flex items-center gap-3 rounded-full border border-white/10 bg-[#07111f]/80 px-5 py-3">
          <ShieldCheck className="h-4 w-4 text-emerald-300" />
          <div className="text-sm">
            <p className="text-white">{currentUser.fullName}</p>
            <p className="text-muted-foreground">
              {currentUser.role.replace("_", " ")} at {tenantName}
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
