import { useQuery } from "@tanstack/react-query";

import { UpcomingTouches } from "@/components/dashboard/upcoming-touches";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { fetchMonthlyTouches } from "@/lib/api";

export default function MonthlyTouchesPage() {
  const { data } = useQuery({
    queryKey: ["monthly-touches"],
    queryFn: fetchMonthlyTouches,
  });

  return (
    <div className="space-y-4">
      <Card className="p-6">
        <Badge>Workflow</Badge>
        <h2 className="mt-4 font-display text-3xl text-white">Monthly Touch lifecycle</h2>
        <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
          Pre-meeting intelligence, approvals, recap generation, QA auditing, and learning updates are designed as
          an observable sequence instead of disconnected tasks.
        </p>
      </Card>
      {data ? <UpcomingTouches items={data} /> : null}
    </div>
  );
}
