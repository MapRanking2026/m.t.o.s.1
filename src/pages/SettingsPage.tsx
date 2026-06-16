import { OwnershipSyncPanel } from "@/components/settings/ownership-sync-panel";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

const settingsGroups = [
  "Tenant configuration and environment isolation",
  "AI provider routing defaults and fallback policy",
  "ClickUp ownership sync cadence and exception handling",
  "Supabase RLS policy verification and audit logs",
];

export default function SettingsPage() {
  return (
    <div className="space-y-4">
      <Card className="p-6">
        <Badge>Admin Controls</Badge>
        <h2 className="mt-4 font-display text-3xl text-white">Production guardrails</h2>
        <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
          MTOS is designed for agencies with strict ownership boundaries, approval flows, and environment-driven
          controls.
        </p>
      </Card>

      <OwnershipSyncPanel />

      <div className="grid gap-4 xl:grid-cols-2">
        {settingsGroups.map((item) => (
          <Card key={item} className="p-6">
            <p className="font-medium text-white">{item}</p>
            <p className="mt-2 text-sm text-muted-foreground">
              Scaffolded in this build as architecture-backed placeholders ready for phase-specific implementation.
            </p>
          </Card>
        ))}
      </div>
    </div>
  );
}
