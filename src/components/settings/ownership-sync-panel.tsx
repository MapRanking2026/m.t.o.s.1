import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, RefreshCw, ShieldAlert, UserRoundSearch } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  fetchClickUpIntegrationStatus,
  fetchOwnershipExceptions,
  fetchOwnershipSyncSummary,
  runOwnershipSync,
} from "@/lib/api";
import { useAppStore } from "@/store/app-store";

export function OwnershipSyncPanel() {
  const queryClient = useQueryClient();
  const actingRole = useAppStore((state) => state.actingIdentity.role);
  const isAdmin = actingRole === "admin";

  const summaryQuery = useQuery({
    queryKey: ["ownership-summary"],
    queryFn: fetchOwnershipSyncSummary,
    enabled: isAdmin,
  });

  const exceptionsQuery = useQuery({
    queryKey: ["ownership-exceptions"],
    queryFn: fetchOwnershipExceptions,
    enabled: isAdmin,
  });

  const clickupStatusQuery = useQuery({
    queryKey: ["clickup-status"],
    queryFn: fetchClickUpIntegrationStatus,
    enabled: isAdmin,
  });

  const syncMutation = useMutation({
    mutationFn: runOwnershipSync,
    onSuccess: () => {
      toast.success("Ownership sync completed");
      void queryClient.invalidateQueries({ queryKey: ["ownership-summary"] });
      void queryClient.invalidateQueries({ queryKey: ["ownership-exceptions"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard-overview"] });
      void queryClient.invalidateQueries({ queryKey: ["clients"] });
    },
    onError: (error) => {
      if (error instanceof Error && error.message) {
        toast.error(error.message);
        return;
      }
      toast.error("Ownership sync failed");
    },
  });

  if (!isAdmin) {
    return (
      <Card className="p-6">
        <div className="flex items-start gap-4">
          <div className="rounded-full border border-amber-300/20 bg-amber-300/10 p-3">
            <ShieldAlert className="h-5 w-5 text-amber-200" />
          </div>
          <div>
            <p className="font-medium text-white">Admin-only ownership administration</p>
            <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
              Account Managers can only see assigned clients. Switch to the admin identity above to review ClickUp
              ownership sync results and unresolved assignment exceptions.
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
      <Card className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <Badge>Ownership Sync</Badge>
            <h3 className="mt-4 font-display text-3xl text-white">ClickUp Client Health Tracker</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Source-of-truth ownership sync runs every 15 minutes and controls MTOS client visibility.
            </p>
            {clickupStatusQuery.data ? (
              <p className="mt-3 text-xs uppercase tracking-[0.18em] text-muted-foreground">
                {clickupStatusQuery.data.configured ? "ClickUp connected" : "ClickUp not configured"}
              </p>
            ) : null}
          </div>
          <Button
            onClick={() => syncMutation.mutate()}
            disabled={syncMutation.isPending || clickupStatusQuery.data?.configured === false}
          >
            <RefreshCw className={`h-4 w-4 ${syncMutation.isPending ? "animate-spin" : ""}`} />
            Run Sync
          </Button>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Provider</p>
            <p className="mt-2 text-white">{summaryQuery.data?.provider ?? "Loading"}</p>
            <p className="mt-1 text-sm text-muted-foreground">{summaryQuery.data?.source ?? "..."}</p>
          </div>
          <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Last Run</p>
            <p className="mt-2 text-white">{summaryQuery.data?.lastRunAt ?? "Loading"}</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Every {summaryQuery.data?.cadenceMinutes ?? 15} minutes
            </p>
          </div>
          <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Matched Clients</p>
            <p className="mt-2 text-white">{summaryQuery.data?.matchedClients ?? "--"}</p>
          </div>
          <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Exceptions</p>
            <p className="mt-2 text-white">{summaryQuery.data?.exceptionCount ?? "--"}</p>
            <p className="mt-1 text-sm text-muted-foreground">
              {summaryQuery.data?.unmatchedClients ?? "--"} unmatched assignments
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-full border border-rose-300/20 bg-rose-300/10 p-3">
            <AlertTriangle className="h-5 w-5 text-rose-200" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Exception Queue</p>
            <h3 className="font-display text-3xl text-white">Unresolved AM mappings</h3>
          </div>
        </div>

        <div className="mt-6 space-y-3">
          {exceptionsQuery.data?.map((exception) => (
            <div key={exception.id} className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-medium text-white">{exception.clientName}</p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    ClickUp AM: {exception.externalAccountManager}
                  </p>
                </div>
                <Badge className="border-rose-300/20 bg-rose-300/10 text-rose-100">{exception.status}</Badge>
              </div>
              <p className="mt-3 text-sm text-muted-foreground">{exception.reason}</p>
              <div className="mt-4 flex items-center gap-2 text-sm text-emerald-100">
                <UserRoundSearch className="h-4 w-4" />
                <span>Suggested MTOS user: {exception.suggestedUserName ?? "No match found"}</span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
