import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { ClientHealthTable } from "@/components/dashboard/client-health-table";
import { MetricCard } from "@/components/dashboard/metric-card";
import { UpcomingTouches } from "@/components/dashboard/upcoming-touches";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { fetchDashboardOverview } from "@/lib/api";

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard-overview"],
    queryFn: fetchDashboardOverview,
  });

  if (isLoading || !data) {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="h-40 animate-pulse rounded-[28px] bg-white/5" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.4fr)_minmax(420px,1fr)]">
        <Card className="overflow-hidden p-6">
          <div className="grid gap-8 lg:grid-cols-[1.2fr_minmax(0,1fr)]">
            <div>
              <p className="text-sm text-muted-foreground">Morning Brief</p>
              <h2 className="mt-3 font-display text-5xl leading-none text-white">
                Run every client relationship from one operating rhythm.
              </h2>
              <p className="mt-4 max-w-xl text-sm text-muted-foreground">
                MTOS turns recurring Monthly Touch meetings into a measurable operating system with approvals,
                intelligence, QA, and learning loops.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Button asChild>
                  <Link to="/monthly-touches">
                    Review Today&apos;s Briefs
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild variant="secondary">
                  <Link to="/prompts">
                    Prompt Center
                    <Sparkles className="h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </div>

            <div className="grid gap-3">
              {data.metrics.slice(0, 2).map((metric) => (
                <MetricCard key={metric.id} metric={metric} />
              ))}
            </div>
          </div>
        </Card>

        <UpcomingTouches items={data.monthlyTouches.slice(0, 4)} />
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {data.metrics.map((metric) => (
          <MetricCard key={metric.id} metric={metric} />
        ))}
      </section>

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.3fr)_minmax(420px,1fr)]">
        <ClientHealthTable clients={data.clients} />
        <ActivityFeed items={data.activity} />
      </section>
    </div>
  );
}
