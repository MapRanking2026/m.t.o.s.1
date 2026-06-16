import { BrainCircuit, FileOutput, ShieldCheck, TriangleAlert, Zap } from "lucide-react";

import { Card } from "@/components/ui/card";
import type { ActivityRecord } from "@/types/mtos";

const activityIcons = {
  brief: BrainCircuit,
  sync: Zap,
  risk: TriangleAlert,
  qa: ShieldCheck,
  recap: FileOutput,
};

interface ActivityFeedProps {
  items: ActivityRecord[];
}

export function ActivityFeed({ items }: ActivityFeedProps) {
  return (
    <Card className="p-6">
      <div>
        <p className="text-sm text-muted-foreground">Live Operations</p>
        <h2 className="mt-1 font-display text-2xl text-white">AI and sync activity</h2>
      </div>

      <div className="mt-6 space-y-4">
        {items.map((item) => {
          const Icon = activityIcons[item.kind];

          return (
            <div key={item.id} className="flex gap-4 rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
              <div className="mt-1 rounded-full border border-white/10 bg-white/5 p-2">
                <Icon className="h-4 w-4 text-emerald-200" />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <p className="font-medium text-white">{item.title}</p>
                  <span className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{item.at}</span>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">{item.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
