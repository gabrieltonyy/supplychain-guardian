"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
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

const supplierProfiles: Record<
  string,
  {
    incident: string;
    severity: "Critical" | "High" | "Medium" | "Low";
    impact: string;
    exposure: string;
    action: string;
    operationalImpact: string[];
  }
> = {
  "SUP-CN-001": {
    incident: "China semiconductor supply disruption",
    severity: "Critical",
    impact: "Projected 12-day semiconductor delivery delay",
    exposure: "$1.4M",
    action: "Approve alternate sourcing and generate emergency procurement RFQ.",
    operationalImpact: [
      "Inventory depletion risk within 5 days",
      "Manufacturing delays likely for semiconductor-dependent products",
      "Potential SLA breach for downstream customers",
    ],
  },
  "SUP-DE-001": {
    incident: "Backup supplier continuity review",
    severity: "Low",
    impact: "Supplier stable and available as mitigation fallback",
    exposure: "$620K",
    action: "Maintain supplier as preferred alternate sourcing option.",
    operationalImpact: [
      "Available for partial sourcing redistribution",
      "Low operational risk detected",
      "Strong mitigation candidate",
    ],
  },
  "SUP-IN-001": {
    incident: "Lead-time anomaly investigation",
    severity: "Medium",
    impact: "Supplier lead time increased beyond expected baseline",
    exposure: "$510K",
    action: "Request revised fulfillment timeline and compare alternatives.",
    operationalImpact: [
      "Possible downstream scheduling delays",
      "Inventory replenishment timing uncertainty",
      "Escalation not yet required",
    ],
  },
  "SUP-IR-001": {
    incident: "Trade compliance hold",
    severity: "High",
    impact: "Workflow blocked pending compliance and trade-control review",
    exposure: "$420K",
    action: "Escalate to compliance officer before RFQ execution.",
    operationalImpact: [
      "Execution blocked by policy controls",
      "Legal/compliance review required",
      "Procurement workflow paused",
    ],
  },
};

function getSeverityClass(severity: string) {
  switch (severity) {
    case "Critical":
      return "bg-red-50 text-red-700 border-red-200";
    case "High":
      return "bg-orange-50 text-orange-700 border-orange-200";
    case "Medium":
      return "bg-amber-50 text-amber-700 border-amber-200";
    default:
      return "bg-emerald-50 text-emerald-700 border-emerald-200";
  }
}

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

  const supplierId =
    workflow?.supplier_id || replayData?.supplier_id || "UNKNOWN-SUPPLIER";

  const profile =
    supplierProfiles[supplierId] ?? {
      incident: "Operational supplier investigation",
      severity: "Medium" as const,
      impact: "Operational impact pending review",
      exposure: "TBD",
      action: "Review workflow recommendations and mitigation plan.",
      operationalImpact: ["Operational context not available"],
    };

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

        <Button variant="outline">Export Incident Report</Button>
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
              <SummaryTile label="Supplier" value={supplierId} icon={FileWarning} />

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
                value={workflow?.status ?? "Unknown"}
                icon={CheckCircle2}
              />

              <SummaryTile
                label="Recommended Action"
                value={profile.action}
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
                    {profile.action}
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">
                    <Button>Approve Recommendation</Button>

                    <Button variant="outline">Request Human Review</Button>

                    <Button variant="outline">Escalate</Button>
                  </div>
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
            supplierId={supplierId}
            status={workflow?.status}
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