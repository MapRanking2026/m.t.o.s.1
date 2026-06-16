import { useEffect } from "react";
import { ArrowLeft, CircleAlert, RefreshCcw, ShieldCheck, Sparkles } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { fetchClientWorkspace, syncClientIntelligence } from "@/lib/api";
import { useAppStore } from "@/store/app-store";

export default function ClientWorkspacePage() {
  const { clientId } = useParams();
  const setActiveClientId = useAppStore((state) => state.setActiveClientId);
  const queryClient = useQueryClient();

  useEffect(() => {
    setActiveClientId(clientId ?? null);

    return () => {
      setActiveClientId(null);
    };
  }, [clientId, setActiveClientId]);

  const { data, error, isLoading } = useQuery({
    queryKey: ["client-workspace", clientId],
    queryFn: () => fetchClientWorkspace(clientId ?? ""),
    enabled: Boolean(clientId),
  });

  const syncMutation = useMutation({
    mutationFn: () => syncClientIntelligence(clientId ?? ""),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["client-workspace", clientId] });
      toast.success("ClickUp intelligence refreshed");
    },
    onError: (mutationError: Error) => {
      toast.error(mutationError.message);
    },
  });

  if (isLoading) {
    return <div className="h-72 animate-pulse rounded-[28px] bg-white/5" />;
  }

  if (!clientId || !data) {
    return (
      <Card className="p-6">
        <Badge className="border-rose-400/20 bg-rose-400/10 text-rose-100">Workspace Unavailable</Badge>
        <h2 className="mt-4 font-display text-3xl text-white">Client workspace not found</h2>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          The selected client is outside your ownership scope or is no longer available.
        </p>
        {error instanceof Error ? <p className="mt-4 text-sm text-rose-200">{error.message}</p> : null}
        <Button asChild className="mt-6">
          <Link to="/clients">
            <ArrowLeft className="h-4 w-4" />
            Back to clients
          </Link>
        </Button>
      </Card>
    );
  }

  const { client, intelligenceSummary, intelligenceSnapshot, monthlyTouches, priorityActions, visibilityScope } = data;
  const syncStatusLabel =
    intelligenceSnapshot?.syncStatus === "connected"
      ? "Connected"
      : intelligenceSnapshot?.syncStatus === "warning"
        ? "Needs Attention"
        : intelligenceSnapshot?.syncStatus === "not_found"
          ? "No Match"
          : "Not Synced";

  return (
    <div className="space-y-4">
      <Card className="overflow-hidden p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-3xl">
            <Badge>Client Workspace</Badge>
            <h2 className="mt-4 font-display text-4xl text-white">{client.name}</h2>
            <p className="mt-3 text-sm text-muted-foreground">{intelligenceSummary}</p>
          </div>
          <Button asChild variant="secondary">
            <Link to="/clients">
              <ArrowLeft className="h-4 w-4" />
              Back to portfolio
            </Link>
          </Button>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Card className="p-5">
            <p className="text-sm text-muted-foreground">Health Score</p>
            <p className="mt-3 font-display text-4xl text-white">{client.healthScore}</p>
          </Card>
          <Card className="p-5">
            <p className="text-sm text-muted-foreground">Risk Level</p>
            <p className="mt-3 font-display text-4xl text-white">{client.riskLevel}</p>
          </Card>
          <Card className="p-5">
            <p className="text-sm text-muted-foreground">Owner</p>
            <p className="mt-3 font-display text-3xl text-white">{client.owner}</p>
          </Card>
          <Card className="p-5">
            <p className="text-sm text-muted-foreground">Next Touch</p>
            <p className="mt-3 font-display text-3xl text-white">{client.nextTouchAt}</p>
          </Card>
        </div>
      </Card>

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_420px]">
        <Card className="p-6">
          <div className="flex items-center gap-3">
            <Sparkles className="h-4 w-4 text-cyan-200" />
            <div>
              <p className="text-sm text-muted-foreground">Priority Actions</p>
              <h3 className="font-display text-2xl text-white">What needs attention next</h3>
            </div>
          </div>
          <div className="mt-6 space-y-3">
            {priorityActions.map((action) => (
              <div key={action} className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-4 text-sm text-white">
                {action}
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3">
            <ShieldCheck className="h-4 w-4 text-emerald-200" />
            <div>
              <p className="text-sm text-muted-foreground">Visibility Scope</p>
              <h3 className="font-display text-2xl text-white">Access enforcement</h3>
            </div>
          </div>
          <p className="mt-6 text-sm text-muted-foreground">{visibilityScope}</p>
          <div className="mt-6 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-4 text-sm text-emerald-50">
            Ownership is enforced before this page loads, so inaccessible client IDs return no workspace.
          </div>
        </Card>
      </section>

      <Card className="p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <Sparkles className="h-4 w-4 text-cyan-200" />
            <div>
              <p className="text-sm text-muted-foreground">ClickUp Intelligence</p>
              <h3 className="font-display text-2xl text-white">Latest synced tracker context</h3>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Badge
              className={
                intelligenceSnapshot?.syncStatus === "connected"
                  ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-50"
                  : intelligenceSnapshot?.syncStatus === "warning"
                    ? "border-amber-400/20 bg-amber-400/10 text-amber-50"
                    : "border-white/10 bg-white/5 text-muted-foreground"
              }
            >
              {syncStatusLabel}
            </Badge>
            <Button onClick={() => syncMutation.mutate()} disabled={!clientId || syncMutation.isPending}>
              <RefreshCcw className={`h-4 w-4 ${syncMutation.isPending ? "animate-spin" : ""}`} />
              {syncMutation.isPending ? "Syncing..." : "Refresh ClickUp"}
            </Button>
          </div>
        </div>

        {intelligenceSnapshot ? (
          <>
            <p className="mt-6 text-sm text-muted-foreground">{intelligenceSnapshot.summary}</p>

            <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <Card className="p-5">
                <p className="text-sm text-muted-foreground">Source</p>
                <p className="mt-3 font-display text-3xl text-white">{intelligenceSnapshot.source}</p>
              </Card>
              <Card className="p-5">
                <p className="text-sm text-muted-foreground">Task Status</p>
                <p className="mt-3 font-display text-3xl text-white">{intelligenceSnapshot.taskStatus ?? "Unknown"}</p>
              </Card>
              <Card className="p-5">
                <p className="text-sm text-muted-foreground">Account Manager</p>
                <p className="mt-3 font-display text-3xl text-white">{intelligenceSnapshot.accountManager ?? "Missing"}</p>
              </Card>
              <Card className="p-5">
                <p className="text-sm text-muted-foreground">Last Sync</p>
                <p className="mt-3 font-display text-3xl text-white">{intelligenceSnapshot.syncedAt}</p>
              </Card>
            </div>

            <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
              <div className="space-y-3">
                {intelligenceSnapshot.signals.length > 0 ? (
                  intelligenceSnapshot.signals.map((signal) => (
                    <div
                      key={signal}
                      className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-4 text-sm text-white"
                    >
                      {signal}
                    </div>
                  ))
                ) : (
                  <div className="rounded-2xl border border-dashed border-white/10 px-4 py-6 text-sm text-muted-foreground">
                    No normalized ClickUp signals were captured in the latest sync.
                  </div>
                )}
              </div>
              <Card className="p-5">
                <p className="text-sm text-muted-foreground">Tracker Reference</p>
                <p className="mt-3 text-sm text-white">{intelligenceSnapshot.clickupTaskName ?? "No ClickUp task matched"}</p>
                <p className="mt-4 text-sm text-muted-foreground">Priority</p>
                <p className="mt-2 text-sm text-white">{intelligenceSnapshot.taskPriority ?? "Not set"}</p>
                <p className="mt-4 text-sm text-muted-foreground">Last ClickUp Activity</p>
                <p className="mt-2 text-sm text-white">{intelligenceSnapshot.lastActivityAt ?? "Unknown"}</p>
                <p className="mt-4 text-sm text-muted-foreground">Due Date</p>
                <p className="mt-2 text-sm text-white">{intelligenceSnapshot.dueAt ?? "Not set"}</p>
                {intelligenceSnapshot.clickupTaskUrl ? (
                  <Button asChild variant="secondary" className="mt-5 w-full">
                    <a href={intelligenceSnapshot.clickupTaskUrl} target="_blank" rel="noreferrer">
                      Open ClickUp Task
                    </a>
                  </Button>
                ) : null}
              </Card>
            </div>
          </>
        ) : (
          <div className="mt-6 rounded-2xl border border-dashed border-white/10 px-4 py-6 text-sm text-muted-foreground">
            No ClickUp intelligence snapshot has been synced for this client yet.
          </div>
        )}
      </Card>

      <Card className="p-6">
        <div className="flex items-center gap-3">
          <CircleAlert className="h-4 w-4 text-amber-200" />
          <div>
            <p className="text-sm text-muted-foreground">Monthly Touch Timeline</p>
            <h3 className="font-display text-2xl text-white">Visible workflow history</h3>
          </div>
        </div>

        <div className="mt-6 space-y-3">
          {monthlyTouches.length > 0 ? (
            monthlyTouches.map((touch) => (
              <div
                key={touch.id}
                className="grid gap-3 rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-4 md:grid-cols-[1.2fr_1fr_1fr]"
              >
                <div>
                  <p className="font-medium text-white">{touch.stage}</p>
                  <p className="text-sm text-muted-foreground">{touch.clientName}</p>
                </div>
                <p className="text-sm text-muted-foreground">{touch.scheduledAt}</p>
                <p className="text-sm text-muted-foreground">{touch.owner}</p>
              </div>
            ))
          ) : (
            <div className="rounded-2xl border border-dashed border-white/10 px-4 py-6 text-sm text-muted-foreground">
              No Monthly Touch records are available for this client yet.
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
