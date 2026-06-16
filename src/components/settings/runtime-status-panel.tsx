import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, DatabaseZap, ServerCog } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { fetchRuntimeStatus } from "@/lib/api";

const statusClasses = {
  ok: "border-emerald-300/20 bg-emerald-300/10 text-emerald-100",
  warning: "border-amber-300/20 bg-amber-300/10 text-amber-100",
  error: "border-rose-300/20 bg-rose-300/10 text-rose-100",
};

export function RuntimeStatusPanel() {
  const { data } = useQuery({
    queryKey: ["runtime-status"],
    queryFn: fetchRuntimeStatus,
  });

  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
      <Card className="p-6">
        <div className="flex items-start gap-4">
          <div className="rounded-full border border-sky-300/20 bg-sky-300/10 p-3">
            <ServerCog className="h-5 w-5 text-sky-100" />
          </div>
          <div>
            <Badge>Runtime Status</Badge>
            <h3 className="mt-4 font-display text-3xl text-white">Phase 1 cutover readiness</h3>
            <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
              Confirms whether the API is still using in-memory data or is ready to operate against Supabase-backed
              tenant storage.
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Environment</p>
            <p className="mt-2 text-white">{data?.environment ?? "Loading"}</p>
          </div>
          <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Repository Mode</p>
            <p className="mt-2 text-white">{data?.repositoryMode ?? "Loading"}</p>
          </div>
          <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Supabase Config</p>
            <p className="mt-2 text-white">{data?.supabaseConfigured ? "Configured" : "Not configured"}</p>
          </div>
          <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">RLS/Table Readiness</p>
            <p className="mt-2 text-white">{data?.supabaseRlsReady ? "Ready" : "Needs setup"}</p>
          </div>
        </div>

        <div className="mt-6 rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Recommended Next Step</p>
          <p className="mt-2 text-sm text-white">{data?.recommendedNextStep ?? "Loading runtime guidance..."}</p>
        </div>
      </Card>

      <Card className="p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-full border border-emerald-300/20 bg-emerald-300/10 p-3">
            <DatabaseZap className="h-5 w-5 text-emerald-100" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">System Checks</p>
            <h3 className="font-display text-3xl text-white">Live runtime probes</h3>
          </div>
        </div>

        <div className="mt-6 space-y-3">
          {data?.checks.map((check) => (
            <div key={check.key} className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-medium text-white">{check.label}</p>
                  <p className="mt-2 text-sm text-muted-foreground">{check.detail}</p>
                </div>
                <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs ${statusClasses[check.status]}`}>
                  {check.status === "ok" ? (
                    <CheckCircle2 className="h-3.5 w-3.5" />
                  ) : (
                    <AlertTriangle className="h-3.5 w-3.5" />
                  )}
                  {check.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
