import { ChevronRight } from "lucide-react";
import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { useAppStore } from "@/store/app-store";
import type { ClientRecord } from "@/types/mtos";

interface ClientHealthTableProps {
  clients: ClientRecord[];
}

export function ClientHealthTable({ clients }: ClientHealthTableProps) {
  const { activeClientId, setActiveClientId } = useAppStore();

  return (
    <Card className="overflow-hidden">
      <div className="border-b border-white/10 px-6 py-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Client Health Radar</p>
            <h2 className="mt-1 font-display text-2xl text-white">Risk, ownership, and next-touch execution</h2>
          </div>
          <Badge>Ownership Enforced</Badge>
        </div>
      </div>

      <div className="divide-y divide-white/10">
        {clients.map((client) => (
          <Link
            key={client.id}
            to={`/clients/${client.id}`}
            className={`grid w-full grid-cols-[1.5fr_repeat(4,1fr)_auto] items-center gap-4 px-6 py-4 text-left transition hover:bg-white/[0.03] ${
              activeClientId === client.id ? "bg-white/[0.05]" : ""
            }`}
            onClick={() => setActiveClientId(client.id)}
          >
            <div>
              <p className="font-medium text-white">{client.name}</p>
              <p className="text-sm text-muted-foreground">{client.owner}</p>
            </div>
            <div className="text-sm text-muted-foreground">{client.healthScore}/100</div>
            <div className="text-sm text-muted-foreground">{client.riskLevel}</div>
            <div className="text-sm text-muted-foreground">{client.nextTouchAt}</div>
            <div className="text-sm text-muted-foreground">{client.topOpportunity}</div>
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          </Link>
        ))}
      </div>
    </Card>
  );
}
