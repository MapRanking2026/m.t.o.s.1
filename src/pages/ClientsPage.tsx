import { useQuery } from "@tanstack/react-query";

import { ClientHealthTable } from "@/components/dashboard/client-health-table";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { fetchClients } from "@/lib/api";

export default function ClientsPage() {
  const { data } = useQuery({
    queryKey: ["clients"],
    queryFn: fetchClients,
  });

  return (
    <div className="space-y-4">
      <Card className="p-6">
        <Badge>Client 360</Badge>
        <h2 className="mt-4 font-display text-3xl text-white">Assigned client portfolio</h2>
        <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
          Ownership visibility, health, next touch timing, and expansion opportunities are enforced at the API
          boundary and reflected here.
        </p>
      </Card>
      {data ? <ClientHealthTable clients={data} /> : null}
    </div>
  );
}
