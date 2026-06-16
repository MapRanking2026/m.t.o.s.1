import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { fetchPromptTemplates } from "@/lib/api";

export default function PromptCenterPage() {
  const { data } = useQuery({
    queryKey: ["prompts"],
    queryFn: fetchPromptTemplates,
  });

  return (
    <div className="space-y-4">
      <Card className="p-6">
        <Badge>Prompt Management Center</Badge>
        <h2 className="mt-4 font-display text-3xl text-white">No prompt hardcoding</h2>
        <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
          Prompt templates are versioned, auditable, and mapped to workflow categories so AI behavior can be changed
          without deploying code.
        </p>
      </Card>

      <div className="grid gap-4 xl:grid-cols-2">
        {data?.map((prompt) => (
          <Card key={prompt.id} className="p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-display text-2xl text-white">{prompt.name}</p>
                <p className="mt-2 text-sm text-muted-foreground">{prompt.category}</p>
              </div>
              <Badge>{prompt.status}</Badge>
            </div>
            <div className="mt-6 grid grid-cols-2 gap-3 text-sm text-muted-foreground">
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-xs uppercase tracking-[0.18em]">Provider</p>
                <p className="mt-2 text-white">{prompt.provider}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-xs uppercase tracking-[0.18em]">Version</p>
                <p className="mt-2 text-white">{prompt.version}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
