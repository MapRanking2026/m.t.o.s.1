import { ArrowDownRight, ArrowRight, ArrowUpRight } from "lucide-react";

import { Card } from "@/components/ui/card";
import type { MetricCard as MetricCardType } from "@/types/mtos";

const trendIcon = {
  up: ArrowUpRight,
  down: ArrowDownRight,
  stable: ArrowRight,
};

interface MetricCardProps {
  metric: MetricCardType;
}

export function MetricCard({ metric }: MetricCardProps) {
  const TrendIcon = trendIcon[metric.trend];
  const trendColor =
    metric.trend === "up"
      ? "text-emerald-300"
      : metric.trend === "down"
        ? "text-rose-300"
        : "text-sky-300";

  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <p className="text-sm text-muted-foreground">{metric.label}</p>
        <TrendIcon className={`h-4 w-4 ${trendColor}`} />
      </div>
      <p className="mt-6 font-display text-4xl text-white">{metric.value}</p>
      <p className="mt-2 text-sm text-muted-foreground">{metric.detail}</p>
    </Card>
  );
}
