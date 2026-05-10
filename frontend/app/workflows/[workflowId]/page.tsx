"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  Clock3,
  DollarSign,
  FileWarning,
  Loader2,
  ShieldAlert,
  Sparkles,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { apiClient } from "@/lib/api-client";
import {
  getSeverityClass,
  getSupplierProfile,
} from "@/lib/operational-data";
import { getWorkflowStatus } from "@/lib/utils";
import { normalizeWorkflowReplay } from "@/lib/workflow-normalizers";

import {
  ComplianceCard,
  ExecutionRecordCard,
  MitigationPlanCard,
  ReasoningBadgeRow,
  RiskAssessmentCard,
  TimelineCard,
  WorkflowMetadataCard,
} from "@/components/workflow/workflow-sections";

type ReplayData = {
  supplier_id?: string | null;
  risk_assessment?: Parameters<typeof RiskAssessmentCard>[0]["risk"];
  anomaly_detection?: Parameters<typeof RiskAssessmentCard>[0]["anomaly"];
  reasoning_summary?: string | null;
  ai_reasoning_source?: string | null;
  mitigation_plan?: Parameters<typeof MitigationPlanCard>[0]["plan"];
  mitigation_reasoning_summary?: string | null;
  mitigation_reasoning_source?: string | null;
  execution_record?: Parameters<typeof ExecutionRecordCard>[0]["execution"];
  execution_reasoning_summary?: string | null;
  execution_reasoning_source?: string | null;
  compliance_verdict?: string | null;
  compliance_reasoning_summary?: string | null;
  compliance_reasoning_source?: string | null;
};

function AgentStep({
  title,
  status,
  detail,
}: {
  title: string;
  status: "completed" | "running" | "waiting";
  detail: string;
}) {
  return (
    <div className="flex items-start gap-3 rounded-lg border bg-white p-4">
      <div
        className={`mt-0.5 flex h-8 w-8 items-center justify-center rounded-full ${
          status === "completed"
            ? "bg-emerald-50 text-emerald-700"
            : status === "running"
              ? "bg-blue-50 text-blue-700"
              : "bg-slate-100 text-slate-400"
        }`}
      >
        {status === "completed" ? (
          <CheckCircle2 className="h-4 w-4" />
        ) : status === "running" ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Clock3 className="h-4 w-4" />
        )}
      </div>

      <div>
        <div className="font-semibold text-slate-950">{title}</div>
        <div className="mt-1 text-sm text-slate-500">{detail}</div>
      </div>
    </div>
  );
}

export default function WorkflowDetailPage() {
  const params = useParams();
  const workflowId = String(params.workflowId);
  const [reviewDecision, setReviewDecision] = useState<string | null>(null);

  const workflowQuery = useQuery({
    queryKey: ["workflow-detail", workflowId],
    queryFn: () => apiClient.getWorkflowRun(workflowId),
  });

  const timelineQuery = useQuery({
    queryKey: ["workflow-timeline", workflowId],
    queryFn: () => apiClient.getWorkflowTimeline(workflowId),
  });

  const replayQuery = useQuery({
    queryKey: ["workflow-replay", workflowId],
    queryFn: () => apiClient.getWorkflowReplay(workflowId),
  });

  const isLoading =
    workflowQuery.isLoading || timelineQuery.isLoading || replayQuery.isLoading;

  const error = workflowQuery.error || timelineQuery.error || replayQuery.error;

  const workflow = workflowQuery.data?.workflow_run;
  const timeline = timelineQuery.data;
  const replayResponse = replayQuery.data;
  const replayData = replayResponse?.replay as ReplayData | undefined;
  const normalizedReplay = replayResponse
    ? normalizeWorkflowReplay(replayResponse.replay, workflowId)
    : null;

  const supplierId =
    workflow?.supplier_id ||
    replayData?.supplier_id ||
    normalizedReplay?.supplierId ||
    "UNKNOWN-SUPPLIER";

  const profile = getSupplierProfile(supplierId);
  const workflowStatus = workflow ? getWorkflowStatus(workflow) : "Unknown";

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <Link
            href="/workflows"
            className="mb-4 inline-flex items-center text-sm text-slate-600 hover:text-slate-950"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Incident Management
          </Link>

          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight text-slate-950">
              {profile.incident}
            </h1>

            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${getSeverityClass(
                profile.severity
              )}`}
            >
              {profile.severity}
            </span>
          </div>

          <p className="mt-2 max-w-3xl text-slate-600">
            AI-generated incident investigation with risk analysis, mitigation
            planning, RFQ actions, compliance review, and workflow replay.
          </p>
        </div>

        <Button
          variant="outline"
          onClick={() => setReviewDecision("Incident report marked for export review")}
        >
          Mark Export Review
        </Button>
      </div>

      {isLoading ? (
        <Card>
          <CardContent className="flex items-center gap-2 py-8 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading incident command center
          </CardContent>
        </Card>
      ) : error ? (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="flex items-start gap-3 pt-6">
            <AlertCircle className="mt-0.5 h-5 w-5 text-red-700" />

            <div>
              <div className="font-semibold text-red-950">
                Failed to load incident
              </div>

              <p className="mt-1 text-sm text-red-800">
                {error instanceof Error
                  ? error.message
                  : "Unknown backend error"}
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          <Card className="border-slate-200">
            <CardContent className="grid gap-4 p-6 md:grid-cols-2 xl:grid-cols-5">
              <SummaryTile
                label="Supplier"
                value={`${profile.name} / ${supplierId}`}
                icon={FileWarning}
              />

              <SummaryTile
                label="Estimated Exposure"
                value={profile.exposure}
                icon={DollarSign}
              />

              <SummaryTile
                label="Operational Impact"
                value={profile.impact}
                icon={ShieldAlert}
              />

              <SummaryTile
                label="Workflow Status"
                value={workflowStatus}
                icon={CheckCircle2}
              />

              <SummaryTile
                label="Recommended Action"
                value={profile.recommendedAction}
                icon={Sparkles}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Operational Impact</CardTitle>
              <CardDescription>
                Business-facing interpretation of this incident.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-3">
              {profile.operationalImpact.map((item) => (
                <div
                  key={item}
                  className="rounded-lg border bg-white p-4 text-sm text-slate-700"
                >
                  {item}
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Agent Workflow</CardTitle>
              <CardDescription>
                Execution stages across the multi-agent orchestration pipeline.
              </CardDescription>
            </CardHeader>

            <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <AgentStep
                title="Risk Analyst"
                status="completed"
                detail="Analyzed supplier risk, anomalies, and operational exposure."
              />

              <AgentStep
                title="Mitigation Strategist"
                status="completed"
                detail="Generated alternate sourcing and mitigation recommendations."
              />

              <AgentStep
                title="Execution Agent"
                status="completed"
                detail="Prepared RFQ recommendations and execution actions."
              />

              <AgentStep
                title="Compliance Agent"
                status="completed"
                detail="Validated trade and operational compliance rules."
              />
            </CardContent>
          </Card>

          <Card className="border-emerald-200 bg-emerald-50">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <Sparkles className="mt-0.5 h-5 w-5 text-emerald-700" />

                <div>
                  <div className="font-semibold text-emerald-950">
                    Recommended Decision
                  </div>

                  <div className="mt-1 text-sm text-emerald-800">
                    {profile.recommendedAction}
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">
                    <Button
                      onClick={() =>
                        setReviewDecision("Recommendation approved locally")
                      }
                    >
                      Approve Recommendation
                    </Button>

                    <Button
                      variant="outline"
                      onClick={() =>
                        setReviewDecision("Human review requested locally")
                      }
                    >
                      Request Human Review
                    </Button>

                    <Button
                      variant="outline"
                      onClick={() => setReviewDecision("Escalated locally")}
                    >
                      Escalate
                    </Button>
                  </div>

                  <p className="mt-3 text-xs text-emerald-800">
                    Review-only controls. Decisions are visible in this browser
                    session and are not persisted to the backend.
                  </p>

                  {reviewDecision ? (
                    <div className="mt-3 rounded-md border border-emerald-200 bg-white px-3 py-2 text-sm font-medium text-emerald-900">
                      {reviewDecision}
                    </div>
                  ) : null}
                </div>
              </div>
            </CardContent>
          </Card>

          <ReasoningBadgeRow
            sources={{
              ai: replayData?.ai_reasoning_source,
              mitigation: replayData?.mitigation_reasoning_source,
              execution: replayData?.execution_reasoning_source,
              compliance: replayData?.compliance_reasoning_source,
            }}
          />

          <WorkflowMetadataCard
            workflowId={workflow?.workflow_id}
            supplierId={`${profile.name} / ${supplierId}`}
            status={workflowStatus}
          />

          <RiskAssessmentCard
            risk={replayData?.risk_assessment}
            anomaly={replayData?.anomaly_detection}
            reasoning={replayData?.reasoning_summary}
            source={replayData?.ai_reasoning_source}
          />

          <MitigationPlanCard
            plan={replayData?.mitigation_plan}
            reasoning={replayData?.mitigation_reasoning_summary}
            source={replayData?.mitigation_reasoning_source}
          />

          <ExecutionRecordCard
            execution={replayData?.execution_record}
            reasoning={replayData?.execution_reasoning_summary}
            source={replayData?.execution_reasoning_source}
          />

          <ComplianceCard
            verdict={replayData?.compliance_verdict}
            reasoning={replayData?.compliance_reasoning_summary}
            source={replayData?.compliance_reasoning_source}
          />

          <TimelineCard timeline={timeline?.timeline ?? []} />

          {replayResponse?.replay ? (
            <Card>
              <CardHeader>
                <CardTitle>Technical Audit Data</CardTitle>
                <CardDescription>
                  Raw replay data is available for developers and auditors.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <details className="rounded-lg border bg-slate-50 p-4">
                  <summary className="cursor-pointer text-sm font-semibold text-slate-950">
                    Show raw workflow replay snapshot
                  </summary>
                  <pre className="mt-4 max-h-96 overflow-auto rounded-lg bg-slate-950 p-4 text-xs text-slate-100">
                    {JSON.stringify(replayResponse.replay, null, 2)}
                  </pre>
                </details>
              </CardContent>
            </Card>
          ) : null}
        </>
      )}
    </div>
  );
}

function SummaryTile({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
            {label}
          </div>

          <div className="mt-2 text-sm font-semibold text-slate-950">
            {value}
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-slate-50 p-2 text-slate-600">
          <Icon className="h-4 w-4" />
        </div>
      </div>
    </div>
  );
}
