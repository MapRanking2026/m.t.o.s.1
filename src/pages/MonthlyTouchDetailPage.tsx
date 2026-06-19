import { ArrowLeft, CheckCircle2, Circle, Clock3, Sparkles } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { fetchMonthlyTouchDetail } from "@/lib/api";

function workflowStatusClass(status: "complete" | "current" | "upcoming") {
  if (status === "complete") {
    return "border-cyan-400/30 bg-cyan-400/10 text-cyan-100";
  }
  if (status === "current") {
    return "border-blue-400/30 bg-blue-400/10 text-blue-100";
  }
  return "border-white/10 bg-white/5 text-muted-foreground";
}

function checklistStatusClass(status: "done" | "pending") {
  return status === "done"
    ? "border-cyan-400/20 bg-cyan-400/10 text-cyan-50"
    : "border-white/10 bg-white/[0.03] text-muted-foreground";
}

function artifactStatusLabel(status: "ready" | "in_progress" | "pending_approval") {
  if (status === "ready") {
    return "Ready";
  }
  if (status === "in_progress") {
    return "In Progress";
  }
  return "Pending Approval";
}

function artifactStatusClass(status: "ready" | "in_progress" | "pending_approval") {
  if (status === "ready") {
    return "border-cyan-400/20 bg-cyan-400/10 text-cyan-50";
  }
  if (status === "in_progress") {
    return "border-amber-400/20 bg-amber-400/10 text-amber-50";
  }
  return "border-blue-400/20 bg-blue-400/10 text-blue-50";
}

function promptStatusClass(status: "active" | "fallback" | "missing") {
  if (status === "active") {
    return "border-cyan-400/20 bg-cyan-400/10 text-cyan-50";
  }
  if (status === "fallback") {
    return "border-amber-400/20 bg-amber-400/10 text-amber-50";
  }
  return "border-white/10 bg-white/5 text-muted-foreground";
}

function promptStatusLabel(status: "active" | "fallback" | "missing") {
  if (status === "active") {
    return "Active";
  }
  if (status === "fallback") {
    return "Fallback";
  }
  return "Missing";
}

export default function MonthlyTouchDetailPage() {
  const { touchId } = useParams();
  const { data, isLoading, error } = useQuery({
    queryKey: ["monthly-touch-detail", touchId],
    queryFn: () => fetchMonthlyTouchDetail(touchId ?? ""),
    enabled: Boolean(touchId),
  });

  if (isLoading) {
    return <div className="h-72 animate-pulse rounded-[28px] bg-white/5" />;
  }

  if (!touchId || !data) {
    return (
      <Card className="p-6">
        <Badge className="border-rose-400/20 bg-rose-400/10 text-rose-100">Workflow Unavailable</Badge>
        <h2 className="mt-4 font-display text-3xl text-white">Monthly Touch not found</h2>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          The selected workflow is outside your visibility scope or no longer exists.
        </p>
        {error instanceof Error ? <p className="mt-4 text-sm text-rose-200">{error.message}</p> : null}
        <Button asChild className="mt-6">
          <Link to="/monthly-touches">
            <ArrowLeft className="h-4 w-4" />
            Back to Monthly Touches
          </Link>
        </Button>
      </Card>
    );
  }

  const { touch } = data;

  return (
    <div className="space-y-4">
      <Card className="overflow-hidden p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-3xl">
            <Badge>Monthly Touch Workspace</Badge>
            <h2 className="mt-4 font-display text-4xl text-white">{touch.clientName}</h2>
            <p className="mt-3 text-sm text-muted-foreground">{data.executiveSummary}</p>
          </div>
          <div className="flex flex-wrap gap-3">
            {touch.clientId ? (
              <Button asChild variant="secondary">
                <Link to={`/clients/${touch.clientId}`}>Open Client Workspace</Link>
              </Button>
            ) : null}
            <Button asChild variant="secondary">
              <Link to="/monthly-touches">
                <ArrowLeft className="h-4 w-4" />
                Back to Monthly Touches
              </Link>
            </Button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Card className="p-5">
            <p className="text-sm text-muted-foreground">Stage</p>
            <p className="mt-3 font-display text-3xl text-white">{touch.stage}</p>
          </Card>
          <Card className="p-5">
            <p className="text-sm text-muted-foreground">Scheduled</p>
            <p className="mt-3 font-display text-3xl text-white">{touch.scheduledAt}</p>
          </Card>
          <Card className="p-5">
            <p className="text-sm text-muted-foreground">Owner</p>
            <p className="mt-3 font-display text-3xl text-white">{touch.owner}</p>
          </Card>
          <Card className="p-5">
            <p className="text-sm text-muted-foreground">Account Health</p>
            <p className="mt-3 font-display text-3xl text-white">
              {data.accountHealthScore} · {data.riskLevel} Risk
            </p>
          </Card>
        </div>
      </Card>

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.15fr)_380px]">
        <Card className="p-6">
          <div className="flex items-center gap-3">
            <Sparkles className="h-4 w-4 text-cyan-200" />
            <div>
              <p className="text-sm text-muted-foreground">Workflow Timeline</p>
              <h3 className="font-display text-2xl text-white">Where this Monthly Touch stands</h3>
            </div>
          </div>

          <div className="mt-6 space-y-3">
            {data.workflowSteps.map((step) => (
              <div key={step.id} className={`rounded-2xl border px-4 py-4 ${workflowStatusClass(step.status)}`}>
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium">{step.label}</p>
                  <Badge className={workflowStatusClass(step.status)}>
                    {step.status === "complete" ? "Complete" : step.status === "current" ? "Current" : "Upcoming"}
                  </Badge>
                </div>
                <p className="mt-2 text-sm">{step.detail}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3">
            <Clock3 className="h-4 w-4 text-blue-200" />
            <div>
              <p className="text-sm text-muted-foreground">Next Action</p>
              <h3 className="font-display text-2xl text-white">Operator guidance</h3>
            </div>
          </div>
          <p className="mt-6 rounded-2xl border border-blue-400/20 bg-blue-400/10 p-4 text-sm text-blue-50">
            {data.nextAction}
          </p>

          <div className="mt-6 space-y-3">
            {data.generatedArtifacts.map((artifact) => (
              <div key={artifact.id} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium text-white">{artifact.label}</p>
                  <Badge className={artifactStatusClass(artifact.status)}>{artifactStatusLabel(artifact.status)}</Badge>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">{artifact.detail}</p>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <Card className="p-6">
          <h3 className="font-display text-2xl text-white">Wins And Issues</h3>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <div className="space-y-3">
              <p className="text-sm uppercase tracking-[0.18em] text-cyan-200">Top Wins</p>
              {data.topWins.map((win) => (
                <div key={win} className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-4 text-sm text-cyan-50">
                  {win}
                </div>
              ))}
            </div>
            <div className="space-y-3">
              <p className="text-sm uppercase tracking-[0.18em] text-amber-200">Key Issues</p>
              {data.keyIssues.map((issue) => (
                <div key={issue} className="rounded-2xl border border-amber-400/20 bg-amber-400/10 px-4 py-4 text-sm text-amber-50">
                  {issue}
                </div>
              ))}
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="font-display text-2xl text-white">Recommended Talking Points</h3>
          <div className="mt-6 space-y-3">
            {data.strategicRecommendations.map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-4 text-sm text-white">
                {item}
              </div>
            ))}
          </div>
          <div className="mt-6 space-y-3">
            <p className="text-sm uppercase tracking-[0.18em] text-blue-200">Suggested Client Questions</p>
            {data.suggestedQuestions.map((question) => (
              <div key={question} className="rounded-2xl border border-blue-400/20 bg-blue-400/10 px-4 py-4 text-sm text-blue-50">
                {question}
              </div>
            ))}
          </div>
        </Card>
      </section>

      <Card className="p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h3 className="font-display text-2xl text-white">AI Prompt Stack</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              These active prompt templates currently shape the brief, audit, ticketing, and follow-up outputs for this
              Monthly Touch.
            </p>
          </div>
          <Button asChild variant="secondary">
            <Link to="/prompts">Open Prompt Center</Link>
          </Button>
        </div>
        <div className="mt-6 grid gap-4 xl:grid-cols-2">
          {data.promptStack.map((prompt) => (
            <div key={prompt.purpose} className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium text-white">{prompt.purpose}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{prompt.templateName}</p>
                </div>
                <Badge className={promptStatusClass(prompt.status)}>{promptStatusLabel(prompt.status)}</Badge>
              </div>
              <p className="mt-4 text-sm text-muted-foreground">{prompt.detail}</p>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <div className="rounded-2xl border border-white/10 bg-black/10 p-3">
                  <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Provider</p>
                  <p className="mt-2 text-white">{prompt.provider}</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-black/10 p-3">
                  <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Version</p>
                  <p className="mt-2 text-white">{prompt.version}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="font-display text-2xl text-white">Live Meeting Checklist</h3>
        <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {data.meetingChecklist.map((item) => (
            <div key={item.id} className={`flex items-center gap-3 rounded-2xl border px-4 py-4 ${checklistStatusClass(item.status)}`}>
              {item.status === "done" ? <CheckCircle2 className="h-4 w-4" /> : <Circle className="h-4 w-4" />}
              <span className="text-sm">{item.label}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
