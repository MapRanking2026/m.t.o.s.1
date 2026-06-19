import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { activatePromptVersion, createPromptVersion, fetchPromptDetail, fetchPromptTemplates } from "@/lib/api";

export default function PromptCenterPage() {
  const queryClient = useQueryClient();
  const { data } = useQuery({
    queryKey: ["prompts"],
    queryFn: fetchPromptTemplates,
  });
  const [selectedPromptId, setSelectedPromptId] = useState<string | null>(null);
  const detailQuery = useQuery({
    queryKey: ["prompt-detail", selectedPromptId],
    queryFn: () => fetchPromptDetail(selectedPromptId ?? ""),
    enabled: Boolean(selectedPromptId),
  });

  const activeVersion = useMemo(
    () => detailQuery.data?.versions.find((version) => version.id === detailQuery.data?.activeVersionId) ?? null,
    [detailQuery.data],
  );
  const [systemPrompt, setSystemPrompt] = useState("");
  const [userPrompt, setUserPrompt] = useState("");

  useEffect(() => {
    if (!selectedPromptId && data && data.length > 0) {
      setSelectedPromptId(data[0].id);
    }
  }, [data, selectedPromptId]);

  useEffect(() => {
    setSystemPrompt(activeVersion?.systemPrompt ?? "");
    setUserPrompt(activeVersion?.userPrompt ?? "");
  }, [activeVersion]);

  const saveDraftMutation = useMutation({
    mutationFn: () => createPromptVersion(selectedPromptId ?? "", { systemPrompt, userPrompt }),
    onSuccess: (payload) => {
      toast.success("Draft prompt version saved");
      void queryClient.invalidateQueries({ queryKey: ["prompts"] });
      void queryClient.setQueryData(["prompt-detail", selectedPromptId], payload);
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Could not save prompt draft");
    },
  });

  const activateMutation = useMutation({
    mutationFn: (versionId: string) => activatePromptVersion(selectedPromptId ?? "", versionId),
    onSuccess: (payload) => {
      toast.success("Prompt version activated");
      void queryClient.invalidateQueries({ queryKey: ["prompts"] });
      void queryClient.setQueryData(["prompt-detail", selectedPromptId], payload);
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Could not activate prompt version");
    },
  });

  return (
    <div className="space-y-4">
      <Card className="p-6">
        <Badge>Prompt Management Center</Badge>
        <h2 className="mt-4 font-display text-3xl text-white">No prompt hardcoding</h2>
        <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
          Leadership can edit Monthly Touch AI behavior here, publish new prompt versions, and control which version
          is active without waiting on a code deployment.
        </p>
      </Card>

      <section className="grid gap-4 xl:grid-cols-[360px_minmax(0,1fr)]">
        <Card className="p-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm text-muted-foreground">Prompt Library</p>
              <h3 className="mt-1 font-display text-2xl text-white">Workflow templates</h3>
            </div>
            <Badge>{data?.length ?? 0} Items</Badge>
          </div>

          <div className="mt-6 space-y-3">
            {data?.map((prompt) => (
              <button
                key={prompt.id}
                type="button"
                onClick={() => setSelectedPromptId(prompt.id)}
                className={`w-full rounded-[24px] border p-4 text-left transition ${
                  selectedPromptId === prompt.id
                    ? "border-blue-400/30 bg-blue-400/10"
                    : "border-white/10 bg-white/[0.03] hover:border-white/20 hover:bg-white/[0.05]"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium text-white">{prompt.name}</p>
                    <p className="mt-1 text-sm text-muted-foreground">{prompt.category}</p>
                  </div>
                  <Badge>{prompt.status}</Badge>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                  <div className="rounded-2xl border border-white/10 bg-black/10 p-3">
                    <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Provider</p>
                    <p className="mt-2 text-white">{prompt.provider}</p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-black/10 p-3">
                    <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Active</p>
                    <p className="mt-2 text-white">{prompt.version}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </Card>

        <div className="space-y-4">
          <Card className="p-6">
            {!detailQuery.data ? (
              <div className="rounded-2xl border border-dashed border-white/10 px-4 py-12 text-sm text-muted-foreground">
                Select a prompt template to inspect versions and edit the active draft.
              </div>
            ) : (
              <>
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <Badge>{detailQuery.data.template.category}</Badge>
                    <h3 className="mt-4 font-display text-3xl text-white">{detailQuery.data.template.name}</h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Active version: {detailQuery.data.template.version} · Provider: {detailQuery.data.template.provider}
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <Button
                      variant="secondary"
                      onClick={() => {
                        setSystemPrompt(activeVersion?.systemPrompt ?? "");
                        setUserPrompt(activeVersion?.userPrompt ?? "");
                      }}
                    >
                      Reset To Active
                    </Button>
                    <Button
                      onClick={() => saveDraftMutation.mutate()}
                      disabled={!selectedPromptId || saveDraftMutation.isPending || !systemPrompt.trim() || !userPrompt.trim()}
                    >
                      Save Draft Version
                    </Button>
                  </div>
                </div>

                <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_320px]">
                  <div className="space-y-4">
                    <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">System Prompt</p>
                      <textarea
                        value={systemPrompt}
                        onChange={(event) => setSystemPrompt(event.target.value)}
                        className="mt-3 min-h-40 w-full resize-y rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-400/30"
                      />
                    </div>
                    <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">User Prompt</p>
                      <textarea
                        value={userPrompt}
                        onChange={(event) => setUserPrompt(event.target.value)}
                        className="mt-3 min-h-48 w-full resize-y rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-400/30"
                      />
                    </div>
                  </div>

                  <div className="space-y-3">
                    <p className="text-sm text-muted-foreground">Version History</p>
                    {detailQuery.data.versions.map((version) => (
                      <div key={version.id} className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="font-medium text-white">v{version.versionNumber}</p>
                            <p className="mt-1 text-xs uppercase tracking-[0.18em] text-muted-foreground">
                              {version.createdAt}
                            </p>
                          </div>
                          <Badge
                            className={
                              version.isActive
                                ? "border-blue-400/20 bg-blue-400/10 text-blue-50"
                                : "border-white/10 bg-white/5 text-muted-foreground"
                            }
                          >
                            {version.isActive ? "Active" : "Draft"}
                          </Badge>
                        </div>
                        <p className="mt-4 line-clamp-3 text-sm text-muted-foreground">{version.systemPrompt}</p>
                        <div className="mt-4 flex gap-2">
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => {
                              setSystemPrompt(version.systemPrompt);
                              setUserPrompt(version.userPrompt);
                            }}
                          >
                            Load
                          </Button>
                          {!version.isActive ? (
                            <Button
                              size="sm"
                              onClick={() => activateMutation.mutate(version.id)}
                              disabled={activateMutation.isPending}
                            >
                              Activate
                            </Button>
                          ) : null}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </Card>
        </div>
      </section>
    </div>
  );
}
