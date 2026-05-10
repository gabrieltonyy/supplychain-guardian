import type {
  ComplianceAudit,
  RFQ,
  ReplayPayload,
  RiskAssessment,
  WorkflowRunItem,
} from "@/lib/api-types";
import {
  formatCurrency,
  formatDate,
  getRFQs,
  getRfqTargetPrice,
  getRiskLevel,
  getRiskScore,
  getWorkflowStatus,
  normalizeStatus,
} from "@/lib/utils";
import {
  getSupplierProfile,
  severityFromRiskLevel,
  type Severity,
} from "@/lib/operational-data";

export type NormalizedWorkflowRun = {
  workflowId: string;
  supplierId: string;
  supplierName: string;
  status: string;
  statusLabel: string;
  startedAt: string;
  incident: string;
  severity: Severity;
  impact: string;
  exposure: string;
  recommendedAction: string;
};

export type NormalizedRiskAssessment = {
  score: number | null;
  scoreLabel: string;
  level: RiskAssessment["level"] | null;
  severity: Severity;
  recommendation: string;
};

export type NormalizedRFQ = {
  id: string;
  workflowId?: string | null;
  originalSupplierId?: string | null;
  supplierId: string;
  supplierName: string;
  status: "Pending Approval" | "Approved" | "Compliance Review" | "Draft" | "Rejected";
  price: string;
  leadTime: string;
  risk: string;
  reason: string;
  deadline: string;
  source: "backend" | "mitigation";
};

export type NormalizedComplianceAudit = {
  verdict: string;
  needsReview: boolean;
  summary: string;
};

export type NormalizedWorkflowReplay = {
  workflowId?: string | null;
  supplierId: string;
  risk: NormalizedRiskAssessment | null;
  rfqs: NormalizedRFQ[];
  compliance: NormalizedComplianceAudit | null;
};

export function normalizeWorkflowRun(run: WorkflowRunItem): NormalizedWorkflowRun {
  const profile = getSupplierProfile(run.supplier_id);
  const status = getWorkflowStatus(run);

  return {
    workflowId: run.workflow_id,
    supplierId: run.supplier_id,
    supplierName: profile.name,
    status,
    statusLabel: normalizeStatus(status),
    startedAt: formatDate(run.started_at),
    incident: profile.incident,
    severity: profile.severity,
    impact: profile.impact,
    exposure: profile.exposure,
    recommendedAction: profile.recommendedAction,
  };
}

export function normalizeRiskAssessment(
  risk?: RiskAssessment | null
): NormalizedRiskAssessment | null {
  if (!risk) {
    return null;
  }

  const score = getRiskScore(risk);
  const level = getRiskLevel(risk);

  return {
    score,
    scoreLabel: score !== null ? score.toFixed(1) : "N/A",
    level,
    severity: severityFromRiskLevel(level),
    recommendation:
      risk.recommendation ??
      (level === "CRITICAL" || level === "HIGH"
        ? "Review mitigation options before approving additional sourcing."
        : "Continue monitoring and compare mitigation options if the trend worsens."),
  };
}

export function normalizeRFQ(
  rfq: RFQ,
  context?: {
    workflowId?: string | null;
    originalSupplierId?: string | null;
    fallbackStatus?: NormalizedRFQ["status"];
    reason?: string;
  }
): NormalizedRFQ {
  const rawStatus = normalizeStatus(rfq.status).toLowerCase();
  const status =
    rawStatus.includes("approved") || rawStatus.includes("dispatched")
      ? "Approved"
      : rawStatus.includes("review") || rfq.human_approval_required
        ? "Compliance Review"
        : rawStatus.includes("reject")
          ? "Rejected"
          : rawStatus.includes("draft")
            ? "Draft"
            : context?.fallbackStatus ?? "Pending Approval";

  return {
    id: rfq.rfq_id ?? rfq.id ?? `${rfq.supplier_id ?? "rfq"}-${rfq.generated_at ?? "unknown"}`,
    workflowId: context?.workflowId,
    originalSupplierId: context?.originalSupplierId,
    supplierId: rfq.supplier_id ?? "UNKNOWN-SUPPLIER",
    supplierName: rfq.supplier_name ?? rfq.supplier_id ?? "Unknown supplier",
    status,
    price: formatCurrency(getRfqTargetPrice(rfq)),
    leadTime: formatDate(rfq.response_deadline),
    risk: "See workflow risk",
    reason:
      context?.reason ??
      "RFQ generated from mitigation workflow and awaiting procurement review.",
    deadline: formatDate(rfq.response_deadline),
    source: "backend",
  };
}

export function normalizeComplianceAudit(
  audit?: ComplianceAudit | null,
  verdict?: string | null,
  summary?: string | null
): NormalizedComplianceAudit | null {
  const resolvedVerdict = verdict ?? audit?.verdict;

  if (!resolvedVerdict && !audit) {
    return null;
  }

  const verdictLabel = normalizeStatus(resolvedVerdict ?? "audit logged");
  const lower = verdictLabel.toLowerCase();

  return {
    verdict: verdictLabel,
    needsReview:
      lower.includes("block") ||
      lower.includes("fail") ||
      lower.includes("review") ||
      lower.includes("pending"),
    summary:
      summary ??
      audit?.llm_summary ??
      audit?.verdict_rationale ??
      "Compliance audit evidence is available in the workflow record.",
  };
}

export function normalizeWorkflowReplay(
  replay: ReplayPayload,
  workflowId?: string | null
): NormalizedWorkflowReplay {
  const run = replay.workflow_run;
  const supplierId =
    run?.supplier_id ??
    replay.risk_assessment?.supplier_id ??
    replay.mitigation_plan?.original_supplier_id ??
    "UNKNOWN-SUPPLIER";
  const directRfqs = replay.rfqs.length
    ? replay.rfqs
    : getRFQs(replay.execution_record);

  const normalizedRfqs = directRfqs.map((rfq) =>
    normalizeRFQ(rfq, {
      workflowId: workflowId ?? run?.workflow_id,
      originalSupplierId: supplierId,
      reason: replay.execution_record?.approval_status
        ? `Approval status: ${normalizeStatus(replay.execution_record.approval_status)}`
        : undefined,
    })
  );

  const mitigationRfqs =
    normalizedRfqs.length || !replay.mitigation_plan
      ? []
      : replay.mitigation_plan.recommended_options.map((option, index) => ({
          id: option.option_id ?? option.id ?? option.supplier_id ?? `option-${index + 1}`,
          workflowId: workflowId ?? run?.workflow_id,
          originalSupplierId: supplierId,
          supplierId: option.supplier_id ?? `ALT-SUP-${index + 1}`,
          supplierName:
            option.supplier_name ??
            option.title ??
            option.supplier_id ??
            `Alternative ${index + 1}`,
          status:
            index === 0
              ? ("Pending Approval" as const)
              : ("Draft" as const),
          price:
            option.cost_estimate !== null && option.cost_estimate !== undefined
              ? formatCurrency(option.cost_estimate)
              : option.cost_delta_pct !== null && option.cost_delta_pct !== undefined
                ? `${option.cost_delta_pct > 0 ? "+" : ""}${option.cost_delta_pct.toFixed(1)}%`
                : "TBD",
          leadTime:
            option.lead_time_delta_days !== null &&
            option.lead_time_delta_days !== undefined
              ? `${option.lead_time_delta_days} days delta`
              : option.time_to_implement ?? "TBD",
          risk:
            option.residual_risk_score !== null &&
            option.residual_risk_score !== undefined
              ? option.residual_risk_score.toFixed(1)
              : "TBD",
          reason:
            option.description ??
            "AI-generated supplier alternative from mitigation workflow.",
          deadline: "TBD",
          source: "mitigation" as const,
        }));

  return {
    workflowId: workflowId ?? run?.workflow_id,
    supplierId,
    risk: normalizeRiskAssessment(replay.risk_assessment),
    rfqs: [...normalizedRfqs, ...mitigationRfqs],
    compliance: normalizeComplianceAudit(replay.compliance_audit),
  };
}
