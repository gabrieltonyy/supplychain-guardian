import {
  AlertCircle,
  CheckCircle2,
  Clock,
  FileText,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

import { AMDReasoningBadge } from "@/components/workflow/amd-reasoning-badge";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type {
  ComplianceAudit,
  ExecutionRecord,
  MitigationPlan,
  RFQ,
  RiskAssessment,
  TimelineEvent,
  WorkflowRunItem,
} from "@/lib/api-types";
import {
  countPendingApprovals,
  formatCurrency,
  formatDate,
  getAnomalyInfo,
  getMitigationJustification,
  getOptionKey,
  getOptionLabel,
  getRFQs,
  getRfqTargetPrice,
  getRiskFactors,
  getRiskLevel,
  getRiskLevelBadgeColor,
  getRiskScore,
  getStatusBadgeColor,
  getWorkflowStatus,
  normalizeStatus,
} from "@/lib/utils";

type ReasoningSources = {
  ai?: string | null;
  mitigation?: string | null;
  execution?: string | null;
  compliance?: string | null;
};

export function ReasoningBadgeRow({ sources }: { sources: ReasoningSources }) {
  return (
    <div className="flex flex-wrap gap-2">
      <AMDReasoningBadge label="Risk" source={sources.ai} />
      <AMDReasoningBadge label="Mitigation" source={sources.mitigation} />
      <AMDReasoningBadge label="Execution" source={sources.execution} />
      <AMDReasoningBadge label="Compliance" source={sources.compliance} />
    </div>
  );
}

export function WorkflowMetadataCard({
  run,
  workflowId,
  supplierId,
  status,
}: {
  run?: WorkflowRunItem | null;
  workflowId?: string | null;
  supplierId?: string | null;
  status?: string | null;
}) {
  const resolvedStatus = status ?? (run ? getWorkflowStatus(run) : null);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Workflow Metadata</CardTitle>
        <CardDescription>
          Technical workflow reference for audit, replay, and traceability.
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Workflow ID" value={workflowId ?? run?.workflow_id ?? "N/A"} mono />
        <Metric label="Supplier" value={supplierId ?? run?.supplier_id ?? "N/A"} />

        <div>
          <div className="text-sm text-muted-foreground">Status</div>
          <Badge className={`${getStatusBadgeColor(resolvedStatus)} mt-1 capitalize`}>
            {normalizeStatus(resolvedStatus)}
          </Badge>
        </div>

        <Metric label="Started" value={formatDate(run?.started_at)} />

        {run?.completed_at ? (
          <Metric label="Completed" value={formatDate(run.completed_at)} />
        ) : null}

        {run?.correlation_id ? (
          <Metric label="Correlation ID" value={run.correlation_id} mono />
        ) : null}
      </CardContent>
    </Card>
  );
}

export function RiskAssessmentCard({
  risk,
  anomaly,
  reasoning,
  source,
}: {
  risk?: RiskAssessment | null;
  anomaly?: {
    is_anomaly?: boolean | null;
    anomaly_direction?: string | null;
    direction?: string | null;
    z_score?: number | null;
    statistical_summary?: string | null;
    reason?: string | null;
  } | null;
  reasoning?: string | null;
  source?: string | null;
}) {
  if (!risk) return null;

  const score = getRiskScore(risk);
  const level = getRiskLevel(risk);
  const factors = getRiskFactors(risk);
  const persistedAnomaly = getAnomalyInfo(risk);
  const isAnomaly = anomaly?.is_anomaly ?? persistedAnomaly.isAnomaly;
  const direction = anomaly?.anomaly_direction ?? anomaly?.direction ?? persistedAnomaly.direction;
  const zScore = anomaly?.z_score ?? persistedAnomaly.zScore;
  const anomalyReason =
    anomaly?.statistical_summary ?? anomaly?.reason ?? persistedAnomaly.reason;

  const businessImpact =
    level === "CRITICAL" || level === "HIGH"
      ? "This supplier requires operational review before more sourcing decisions are made."
      : level === "MEDIUM"
        ? "This supplier should remain under monitoring while mitigation options are compared."
        : "This supplier currently appears stable based on the available signals.";

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <CardTitle>Risk Assessment</CardTitle>
            <CardDescription>
              Business-readable supplier risk, anomaly detection, and scoring explanation.
            </CardDescription>
            <div className="mt-2">
              <AMDReasoningBadge label="Risk Analyst" source={source} />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-3xl font-bold">
                {score !== null ? score.toFixed(1) : "N/A"}
              </div>
              <div className="text-xs text-muted-foreground">Risk score</div>
            </div>
            <Badge className={getRiskLevelBadgeColor(level)}>{level ?? "UNKNOWN"}</Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        <div className="rounded-lg border bg-slate-50 p-4">
          <div className="flex items-start gap-3">
            {isAnomaly ? (
              <AlertCircle className="mt-0.5 h-5 w-5 text-orange-600" />
            ) : (
              <CheckCircle2 className="mt-0.5 h-5 w-5 text-green-600" />
            )}

            <div className="min-w-0 flex-1">
              <div className="font-semibold">
                {isAnomaly ? "Operational anomaly detected" : "No major anomaly detected"}
              </div>

              <div className="mt-1 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                {direction ? (
                  <>
                    {direction === "spike" || direction === "increase" ? (
                      <TrendingUp className="h-4 w-4 text-red-500" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-green-500" />
                    )}
                    <span className="capitalize">{direction}</span>
                  </>
                ) : null}

                {zScore !== null && zScore !== undefined ? (
                  <span className="font-mono">Z-score {zScore.toFixed(2)}</span>
                ) : null}
              </div>

              {anomalyReason ? (
                <p className="mt-2 text-sm text-slate-600">{anomalyReason}</p>
              ) : null}
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
          <h4 className="mb-2 font-semibold text-amber-950">Operational Meaning</h4>
          <p className="text-sm text-amber-900">{businessImpact}</p>
        </div>

        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Factor Breakdown
          </h3>

          <div className="space-y-3">
            {factors.length ? (
              factors.map((factor) => (
                <div key={factor.label}>
                  <div className="mb-1 flex items-center justify-between gap-3 text-sm">
                    <span className="font-medium capitalize">
                      {factor.label.replaceAll("_", " ")}
                    </span>
                    <span className="font-semibold">{factor.score.toFixed(1)}</span>
                  </div>

                  <div className="h-2 overflow-hidden rounded-full bg-slate-200">
                    <div
                      className="h-full bg-gradient-to-r from-emerald-500 via-amber-500 to-red-500"
                      style={{ width: `${Math.min(Math.max(factor.score, 0), 100)}%` }}
                    />
                  </div>

                  {factor.rationale ? (
                    <p className="mt-1 text-xs text-muted-foreground">{factor.rationale}</p>
                  ) : null}
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">No factor breakdown returned.</p>
            )}
          </div>
        </div>

        {reasoning || risk.reasoning_summary ? (
          <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
            <h4 className="mb-2 font-semibold text-blue-950">Reasoning Summary</h4>
            <p className="text-sm text-blue-900">{reasoning ?? risk.reasoning_summary}</p>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

export function MitigationPlanCard({
  plan,
  reasoning,
  source,
}: {
  plan?: MitigationPlan | null;
  reasoning?: string | null;
  source?: string | null;
}) {
  if (!plan) return null;

  const justification = reasoning ?? getMitigationJustification(plan);
  const bestOption = plan.recommended_options[0];

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <CardTitle>Mitigation Plan</CardTitle>
            <CardDescription>
              Recommended supplier alternatives and trade-offs for reducing disruption risk.
            </CardDescription>
          </div>
          <AMDReasoningBadge label="Mitigation Strategist" source={source} />
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {bestOption ? (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h4 className="mb-2 font-semibold text-emerald-950">Best Recommended Option</h4>
            <p className="text-sm text-emerald-900">
              {getOptionLabel(bestOption)}
              {bestOption.description ? ` — ${bestOption.description}` : ""}
            </p>
          </div>
        ) : null}

        {justification ? (
          <div className="rounded-lg border border-violet-200 bg-violet-50 p-4">
            <h4 className="mb-2 font-semibold text-violet-950">Strategy Reasoning</h4>
            <p className="text-sm text-violet-900">{justification}</p>
          </div>
        ) : null}

        <div className="grid gap-4 lg:grid-cols-2">
          {plan.recommended_options.length ? (
            plan.recommended_options.map((option, index) => (
              <div key={getOptionKey(option, index)} className="rounded-lg border bg-white p-4">
                <div className="mb-3 flex items-start justify-between gap-3">
                  <div>
                    <h4 className="font-semibold">{getOptionLabel(option)}</h4>

                    {option.description ? (
                      <p className="mt-1 text-sm text-muted-foreground">{option.description}</p>
                    ) : null}
                  </div>

                  {index === 0 ? (
                    <Badge className="bg-emerald-100 text-emerald-800 hover:bg-emerald-100">
                      Recommended
                    </Badge>
                  ) : option.rank ? (
                    <Badge variant="outline">Rank {option.rank}</Badge>
                  ) : null}
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm text-slate-600">
                  <Metric label="Residual risk" value={formatNumber(option.residual_risk_score)} />
                  <Metric label="Confidence" value={formatPercent(option.confidence)} />
                  <Metric label="Cost delta" value={formatSignedPercent(option.cost_delta_pct)} />
                  <Metric label="Lead time" value={formatDays(option.lead_time_delta_days)} />
                  <Metric label="Onboarding" value={formatWeeks(option.onboarding_weeks)} />
                  <Metric label="TOPSIS" value={formatNumber(option.topsis_score)} />
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">No recommended options returned.</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function ExecutionRecordCard({
  execution,
  rfqs,
  reasoning,
  source,
}: {
  execution?: ExecutionRecord | null;
  rfqs?: RFQ[];
  reasoning?: string | null;
  source?: string | null;
}) {
  if (!execution && !rfqs?.length) return null;

  const resolvedRfqs = rfqs?.length ? rfqs : getRFQs(execution);

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <CardTitle>Execution and RFQs</CardTitle>
            <CardDescription>
              RFQ generation, approval status, and procurement follow-through.
            </CardDescription>
          </div>
          <AMDReasoningBadge label="Execution Agent" source={source} />
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {reasoning ? (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h4 className="mb-2 font-semibold text-emerald-950">Execution Reasoning</h4>
            <p className="text-sm text-emerald-900">{reasoning}</p>
          </div>
        ) : null}

        {execution ? (
          <div className="grid gap-3 sm:grid-cols-3">
            <SummaryTile label="RFQs Generated" value={String(resolvedRfqs.length || execution.total_rfqs || 0)} />
            <SummaryTile label="Approval Status" value={normalizeStatus(execution.approval_status)} />
            <SummaryTile label="Pending Approvals" value={String(countPendingApprovals(execution))} />
          </div>
        ) : null}

        <RFQList rfqs={resolvedRfqs} />
      </CardContent>
    </Card>
  );
}

export function ComplianceCard({
  verdict,
  audit,
  reasoning,
  source,
}: {
  verdict?: string | null;
  audit?: ComplianceAudit | null;
  reasoning?: string | null;
  source?: string | null;
}) {
  const resolvedVerdict = verdict ?? audit?.verdict;

  if (!resolvedVerdict && !audit) return null;

  const isBlocked =
    resolvedVerdict?.toLowerCase().includes("block") ||
    resolvedVerdict?.toLowerCase().includes("fail") ||
    resolvedVerdict?.toLowerCase().includes("review");

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <CardTitle>Compliance Audit</CardTitle>
            <CardDescription>
              Regulatory, sanctions, and trade-control result for the workflow.
            </CardDescription>
          </div>
          <AMDReasoningBadge label="Compliance Agent" source={source} />
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div
          className={`rounded-lg border p-4 ${
            isBlocked
              ? "border-orange-200 bg-orange-50"
              : "border-emerald-200 bg-emerald-50"
          }`}
        >
          <div className="flex flex-wrap items-center gap-3">
            <ShieldCheck
              className={`h-6 w-6 ${isBlocked ? "text-orange-700" : "text-emerald-700"}`}
            />
            <div
              className={`text-2xl font-bold uppercase ${
                isBlocked ? "text-orange-950" : "text-emerald-950"
              }`}
            >
              {resolvedVerdict ?? "audit logged"}
            </div>

            {audit?.log_id ? <Badge variant="outline">Log {audit.log_id}</Badge> : null}
          </div>
        </div>

        {reasoning ?? audit?.llm_summary ?? audit?.verdict_rationale ? (
          <div className="rounded-lg border border-orange-200 bg-orange-50 p-4">
            <h4 className="mb-2 font-semibold text-orange-950">Compliance Reasoning</h4>
            <p className="text-sm text-orange-900">
              {reasoning ?? audit?.llm_summary ?? audit?.verdict_rationale}
            </p>
          </div>
        ) : null}

        {audit?.regulatory_results.length ? (
          <div className="grid gap-2">
            {audit.regulatory_results.map((item, index) => (
              <div key={index} className="rounded-md border bg-white p-3 text-sm">
                <div className="font-medium">{String(item.check_type ?? "Regulatory check")}</div>
                <div className="text-muted-foreground">{String(item.details ?? "")}</div>
              </div>
            ))}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

export function TimelineCard({ timeline }: { timeline: TimelineEvent[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Workflow Timeline</CardTitle>
        <CardDescription>
          Chronological audit trail of agent and workflow events.
        </CardDescription>
      </CardHeader>

      <CardContent>
        {timeline.length ? (
          <ol className="relative space-y-4 border-l border-slate-200 pl-5">
            {timeline.map((event) => (
              <li key={event.id} className="relative">
                <span className="absolute -left-[29px] flex h-4 w-4 items-center justify-center rounded-full bg-slate-900 ring-4 ring-white" />

                <div className="rounded-lg border bg-white p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="font-semibold capitalize">
                      {event.event_type.replaceAll("_", " ")}
                    </div>

                    <Badge className={`${getStatusBadgeColor(event.status)} capitalize`}>
                      {event.status}
                    </Badge>
                  </div>

                  <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                    {event.agent_name ? <span>{event.agent_name}</span> : null}

                    <span className="flex items-center gap-1">
                      <Clock className="h-3.5 w-3.5" />
                      {formatDate(event.created_at ?? event.timestamp)}
                    </span>
                  </div>

                  {event.message ? <p className="mt-2 text-sm">{event.message}</p> : null}

                  {event.error_message ? (
                    <p className="mt-2 text-sm text-red-700">{event.error_message}</p>
                  ) : null}
                </div>
              </li>
            ))}
          </ol>
        ) : (
          <p className="text-sm text-muted-foreground">No timeline events returned.</p>
        )}
      </CardContent>
    </Card>
  );
}

export function FinalStateSnapshotCard({ snapshot }: { snapshot: unknown }) {
  if (!snapshot) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Final State Snapshot
        </CardTitle>
        <CardDescription>
          Raw workflow state retained for audit and debugging.
        </CardDescription>
      </CardHeader>

      <CardContent>
        <pre className="max-h-96 overflow-auto rounded-lg bg-slate-950 p-4 text-xs text-slate-100">
          {JSON.stringify(snapshot, null, 2)}
        </pre>
      </CardContent>
    </Card>
  );
}

export function RFQList({ rfqs }: { rfqs: RFQ[] }) {
  if (!rfqs.length) {
    return (
      <div className="rounded-lg border border-dashed p-6 text-center">
        <div className="font-semibold text-slate-950">No RFQs returned</div>
        <p className="mt-1 text-sm text-muted-foreground">
          The workflow did not generate procurement requests for this run.
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-3">
      {rfqs.map((rfq, index) => (
        <div key={rfq.rfq_id ?? rfq.id ?? index} className="rounded-lg border bg-white p-4">
          <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
            <div>
              <div className="font-semibold">RFQ {rfq.rfq_id ?? rfq.id ?? index + 1}</div>
              <div className="text-sm text-muted-foreground">
                {rfq.supplier_name ?? rfq.supplier_id ?? "Unknown supplier"}
              </div>
            </div>

            <Badge variant="outline" className="capitalize">
              {normalizeStatus(rfq.status)}
            </Badge>
          </div>

          <div className="grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
            <Metric label="Target price" value={formatCurrency(getRfqTargetPrice(rfq))} />
            <Metric label="Deadline" value={formatDate(rfq.response_deadline)} />
            <Metric label="Destination" value={rfq.delivery_destination ?? "N/A"} />
            <Metric label="Terms" value={rfq.terms_ref ?? "N/A"} />
          </div>

          {rfq.line_items.length ? (
            <div className="mt-3 rounded-md bg-slate-50 p-3 text-sm">
              <div className="mb-2 font-medium">Line items</div>

              <div className="space-y-1">
                {rfq.line_items.map((item, itemIndex) => (
                  <div key={itemIndex} className="flex flex-wrap justify-between gap-2 text-slate-600">
                    <span>{item.description ?? item.sku ?? "Line item"}</span>
                    <span>
                      {item.quantity ?? "N/A"} {item.unit ?? ""}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          {rfq.human_approval_required ? (
            <div className="mt-3 rounded-md border border-orange-200 bg-orange-50 p-3 text-sm font-medium text-orange-800">
              Human approval required before supplier dispatch.
            </div>
          ) : null}
        </div>
      ))}
    </div>
  );
}

function SummaryTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-slate-50 p-4">
      <div className="text-2xl font-bold capitalize">{value}</div>
      <div className="text-sm text-muted-foreground">{label}</div>
    </div>
  );
}

function Metric({
  label,
  value,
  mono,
}: {
  label: string;
  value: string | number | null | undefined;
  mono?: boolean;
}) {
  return (
    <div className="min-w-0">
      <div className="text-sm text-muted-foreground">{label}</div>
      <div className={`truncate font-medium ${mono ? "font-mono text-xs" : ""}`}>
        {value ?? "N/A"}
      </div>
    </div>
  );
}

function formatNumber(value: number | null | undefined): string {
  return value !== null && value !== undefined ? value.toFixed(2) : "N/A";
}

function formatPercent(value: number | null | undefined): string {
  return value !== null && value !== undefined ? `${Math.round(value * 100)}%` : "N/A";
}

function formatSignedPercent(value: number | null | undefined): string {
  if (value === null || value === undefined) return "N/A";
  return `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;
}

function formatDays(value: number | null | undefined): string {
  return value !== null && value !== undefined ? `${value} days` : "N/A";
}

function formatWeeks(value: number | null | undefined): string {
  return value !== null && value !== undefined ? `${value} weeks` : "N/A";
}