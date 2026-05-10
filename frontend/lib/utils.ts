import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import type {
  ExecutionRecord,
  MitigationPlan,
  RecommendedOption,
  RFQ,
  RiskAssessment,
  RiskLevel,
  WorkflowRunItem,
} from "./api-types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getRiskLevelColor(level: RiskLevel | null | undefined): string {
  switch (level) {
    case "CRITICAL":
      return "bg-red-100 text-red-800 border-red-200";
    case "HIGH":
      return "bg-orange-100 text-orange-800 border-orange-200";
    case "MEDIUM":
      return "bg-yellow-100 text-yellow-800 border-yellow-200";
    case "LOW":
      return "bg-green-100 text-green-800 border-green-200";
    default:
      return "bg-gray-100 text-gray-800 border-gray-200";
  }
}

export function getRiskLevelBadgeColor(level: RiskLevel | null | undefined): string {
  switch (level) {
    case "CRITICAL":
      return "text-red-700 bg-red-50 ring-red-600/20";
    case "HIGH":
      return "text-orange-700 bg-orange-50 ring-orange-600/20";
    case "MEDIUM":
      return "text-yellow-700 bg-yellow-50 ring-yellow-600/20";
    case "LOW":
      return "text-green-700 bg-green-50 ring-green-600/20";
    default:
      return "text-gray-700 bg-gray-50 ring-gray-600/20";
  }
}

export function getStatusBadgeColor(status: string | null | undefined): string {
  switch (status?.toLowerCase()) {
    case "completed":
    case "completed_without_mitigation":
    case "completed_without_execution":
    case "completed_without_audit":
      return "text-green-700 bg-green-50 ring-green-600/20 border-green-200";
    case "running":
      return "text-blue-700 bg-blue-50 ring-blue-600/20 border-blue-200";
    case "failed":
      return "text-red-700 bg-red-50 ring-red-600/20 border-red-200";
    case "pending":
      return "text-yellow-700 bg-yellow-50 ring-yellow-600/20 border-yellow-200";
    default:
      return "text-gray-700 bg-gray-50 ring-gray-600/20 border-gray-200";
  }
}

export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return "N/A";
  try {
    return new Date(dateString).toLocaleString();
  } catch {
    return dateString;
  }
}

export function formatCurrency(amount: number | null | undefined): string {
  if (amount === null || amount === undefined) return "N/A";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

export function isAMDvLLM(source: string | null | undefined): boolean {
  return source === "amd_vllm";
}

export function getReasoningSourceBadge(source: string | null | undefined): {
  label: string;
  color: string;
} {
  if (isAMDvLLM(source)) {
    return {
      label: "AMD ROCm + vLLM",
      color: "text-purple-700 bg-purple-50 ring-purple-600/20",
    };
  }
  return {
    label: source || "Unknown",
    color: "text-gray-700 bg-gray-50 ring-gray-600/20",
  };
}

export function normalizeStatus(status: string | null | undefined): string {
  if (!status) return "unknown";
  return status.replaceAll("_", " ");
}

export function getWorkflowStatus(run: WorkflowRunItem): string {
  return run.workflow_status ?? run.status ?? "unknown";
}

export function getRiskScore(risk: RiskAssessment | null | undefined): number | null {
  if (!risk) return null;
  return risk.score ?? risk.overall_risk_score ?? null;
}

export function getRiskLevel(risk: RiskAssessment | null | undefined): RiskLevel | null {
  if (!risk) return null;
  return risk.level ?? risk.risk_level ?? null;
}

export function getRiskFactors(
  risk: RiskAssessment | null | undefined
): Array<{ label: string; score: number; rationale?: string | null }> {
  if (!risk) return [];

  if (risk.factors?.length) {
    return risk.factors.map((factor) => ({
      label: factor.factor,
      score: factor.score,
      rationale: factor.rationale,
    }));
  }

  return Object.entries(risk.factor_breakdown ?? {}).map(([label, score]) => ({
    label,
    score,
  }));
}

export function getAnomalyInfo(risk: RiskAssessment | null | undefined) {
  return {
    isAnomaly: Boolean(risk?.anomaly_detected),
    direction: risk?.anomaly_direction ?? null,
    zScore: risk?.anomaly_z_score ?? null,
    baselineMean: risk?.anomaly_baseline_mean ?? null,
    reason:
      typeof risk?.anomaly_data?.reason === "string"
        ? risk.anomaly_data.reason
        : null,
  };
}

export function getMitigationJustification(plan: MitigationPlan | null | undefined) {
  return plan?.justification ?? plan?.rationale ?? null;
}

export function getOptionLabel(option: RecommendedOption): string {
  if (option.title) return option.title;
  if (option.supplier_name) return option.supplier_name;
  if (option.supplier_id) return `Switch to ${option.supplier_id}`;
  return option.option_id ?? option.id ?? `Option ${option.rank ?? ""}`.trim();
}

export function getOptionKey(option: RecommendedOption, index: number): string {
  return option.option_id ?? option.id ?? option.supplier_id ?? `option-${index}`;
}

export function getRFQs(execution: ExecutionRecord | null | undefined): RFQ[] {
  if (!execution) return [];
  return execution.rfqs.length ? execution.rfqs : execution.rfqs_created;
}

export function getRfqTargetPrice(rfq: RFQ): number | null {
  if (rfq.target_price !== null && rfq.target_price !== undefined) {
    return rfq.target_price;
  }

  const firstPrice = rfq.line_items.find(
    (item) => item.target_price !== null && item.target_price !== undefined
  )?.target_price;
  return firstPrice ?? null;
}

export function countPendingApprovals(execution: ExecutionRecord | null | undefined): number {
  if (!execution) return 0;
  if (execution.pending_approval !== null && execution.pending_approval !== undefined) {
    return execution.pending_approval;
  }
  return execution.approval_status === "pending_human" ? 1 : 0;
}
