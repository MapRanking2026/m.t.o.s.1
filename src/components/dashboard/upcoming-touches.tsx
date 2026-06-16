import { CalendarClock } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { MonthlyTouchRecord } from "@/types/mtos";

interface UpcomingTouchesProps {
  items: MonthlyTouchRecord[];
}

export function UpcomingTouches({ items }: UpcomingTouchesProps) {
  return (
    <Card className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">Execution Queue</p>
          <h2 className="mt-1 font-display text-2xl text-white">Upcoming Monthly Touches</h2>
        </div>
        <CalendarClock className="h-5 w-5 text-emerald-300" />
      </div>

      <div className="mt-6 space-y-3">
        {items.map((touch) => (
          <div key={touch.id} className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="font-medium text-white">{touch.clientName}</p>
                <p className="text-sm text-muted-foreground">
                  {touch.scheduledAt} · {touch.owner}
                </p>
              </div>
              <Badge className="border-emerald-400/20 bg-emerald-400/10 text-emerald-100">{touch.stage}</Badge>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
