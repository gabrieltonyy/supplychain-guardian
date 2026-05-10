import { z } from "zod";

export const RiskLevelSchema = z.enum(["CRITICAL", "HIGH", "MEDIUM", "LOW"]);
export type RiskLevel = z.infer<typeof RiskLevelSchema>;

export const WorkflowStatusSchema = z.enum([
  "pending",
  "running",
  "completed",
  "completed_without_mitigation",
  "completed_without_execution",
  "completed_without_audit",
  "failed",
  "PENDING",
  "RUNNING",
  "COMPLETED",
  "FAILED",
]);
export type WorkflowStatus = z.infer<typeof WorkflowStatusSchema>;

const NullableRecordSchema = z.record(z.any()).nullable().optional();
const NullableStringSchema = z.string().nullable().optional();
const NullableNumberSchema = z.number().nullable().optional();
const NullableBooleanSchema = z.boolean().nullable().optional();
const FlexibleDateSchema = z.string().nullable().optional();

export const AnomalyDetectionSchema = z
  .object({
    is_anomaly: NullableBooleanSchema,
    anomaly_detected: NullableBooleanSchema,
    anomaly_direction: NullableStringSchema,
    direction: NullableStringSchema,
    z_score: NullableNumberSchema,
    anomaly_z_score: NullableNumberSchema,
    baseline_mean: NullableNumberSchema,
    anomaly_baseline_mean: NullableNumberSchema,
    reason: NullableStringSchema,
    statistical_summary: NullableStringSchema,
  })
  .passthrough();
export type AnomalyDetection = z.infer<typeof AnomalyDetectionSchema>;

export const RiskAssessmentSchema = z
  .object({
    id: NullableStringSchema,
    workflow_id: NullableStringSchema,
    supplier_id: z.string().optional(),
    score: NullableNumberSchema,
    overall_risk_score: NullableNumberSchema,
    level: RiskLevelSchema.optional().nullable(),
    risk_level: RiskLevelSchema.optional().nullable(),
    factor_breakdown: z.record(z.number()).optional().default({}),
    factors: z
      .array(
        z
          .object({
            factor: z.string(),
            score: z.number(),
            weight: z.number().optional().nullable(),
            rationale: NullableStringSchema,
          })
          .passthrough()
      )
      .optional(),
    contributing_signals: z.array(z.string()).optional().default([]),
    anomaly_detected: NullableBooleanSchema,
    anomaly_direction: NullableStringSchema,
    anomaly_z_score: NullableNumberSchema,
    anomaly_baseline_mean: NullableNumberSchema,
    anomaly_data: NullableRecordSchema,
    reasoning_summary: NullableStringSchema,
    recommendation: NullableStringSchema,
    assessed_at: FlexibleDateSchema,
    timestamp: FlexibleDateSchema,
    created_at: FlexibleDateSchema,
  })
  .passthrough();
export type RiskAssessment = z.infer<typeof RiskAssessmentSchema>;

export const RecommendedOptionSchema = z
  .object({
    option_id: NullableStringSchema,
    id: NullableStringSchema,
    title: NullableStringSchema,
    description: NullableStringSchema,
    rank: z.number().optional().nullable(),
    supplier_id: NullableStringSchema,
    supplier_name: NullableStringSchema,
    topsis_score: NullableNumberSchema,
    cost_delta_pct: NullableNumberSchema,
    lead_time_delta_days: z.number().optional().nullable(),
    residual_risk_score: NullableNumberSchema,
    onboarding_weeks: z.number().optional().nullable(),
    confidence: NullableNumberSchema,
    cost_estimate: NullableNumberSchema,
    time_to_implement: NullableStringSchema,
    effectiveness_score: NullableNumberSchema,
    priority: NullableStringSchema,
  })
  .passthrough();
export type RecommendedOption = z.infer<typeof RecommendedOptionSchema>;

export const MitigationPlanSchema = z
  .object({
    id: NullableStringSchema,
    plan_id: NullableStringSchema,
    workflow_id: NullableStringSchema,
    supplier_id: NullableStringSchema,
    original_supplier_id: NullableStringSchema,
    risk_score: NullableNumberSchema,
    risk_level: RiskLevelSchema.optional().nullable(),
    recommended_options: z.array(RecommendedOptionSchema).optional().default([]),
    candidate_suppliers: z.array(z.any()).optional().default([]),
    simulated_scenarios: z.array(z.any()).optional().default([]),
    justification: NullableStringSchema,
    rationale: NullableStringSchema,
    created_by_agent: NullableStringSchema,
    created_at: FlexibleDateSchema,
  })
  .passthrough();
export type MitigationPlan = z.infer<typeof MitigationPlanSchema>;

export const RFQLineItemSchema = z
  .object({
    sku: NullableStringSchema,
    description: NullableStringSchema,
    quantity: z.number().optional().nullable(),
    unit: NullableStringSchema,
    target_price: NullableNumberSchema,
    notes: NullableStringSchema,
  })
  .passthrough();
export type RFQLineItem = z.infer<typeof RFQLineItemSchema>;

export const RFQSchema = z
  .object({
    id: NullableStringSchema,
    rfq_id: z.string().optional(),
    mitigation_plan_id: NullableStringSchema,
    mitigation_option_id: NullableStringSchema,
    supplier_id: NullableStringSchema,
    supplier_name: NullableStringSchema,
    supplier_email: NullableStringSchema,
    line_items: z.array(RFQLineItemSchema).optional().default([]),
    target_price: NullableNumberSchema,
    response_deadline: FlexibleDateSchema,
    delivery_destination: NullableStringSchema,
    terms_ref: NullableStringSchema,
    status: NullableStringSchema,
    version: z.number().optional().nullable(),
    generated_by: NullableStringSchema,
    generated_at: FlexibleDateSchema,
    created_at: FlexibleDateSchema,
    human_approval_required: NullableBooleanSchema,
  })
  .passthrough();
export type RFQ = z.infer<typeof RFQSchema>;

export const ExecutionRecordSchema = z
  .object({
    id: NullableStringSchema,
    workflow_id: NullableStringSchema,
    execution_id: NullableStringSchema,
    mitigation_plan_id: NullableStringSchema,
    rfqs: z.array(RFQSchema).optional().default([]),
    rfqs_created: z.array(RFQSchema).optional().default([]),
    rfq_ids: z.array(z.string()).optional().default([]),
    total_rfqs: z.number().optional().nullable(),
    approved_rfqs: z.number().optional().nullable(),
    pending_approval: z.number().optional().nullable(),
    approval_status: NullableStringSchema,
    approval_decision_at: FlexibleDateSchema,
    approved_by: NullableStringSchema,
    dispatch_log: z.array(z.any()).optional().default([]),
    response_log: z.array(z.any()).optional().default([]),
    created_by_agent: NullableStringSchema,
    created_at: FlexibleDateSchema,
    executed_at: FlexibleDateSchema,
  })
  .passthrough();
export type ExecutionRecord = z.infer<typeof ExecutionRecordSchema>;

export const ComplianceAuditSchema = z
  .object({
    id: NullableStringSchema,
    workflow_id: NullableStringSchema,
    log_id: NullableStringSchema,
    workflow_run_id: NullableStringSchema,
    agent_id: NullableStringSchema,
    agent_version: NullableStringSchema,
    execution_record_id: NullableStringSchema,
    input_hash: NullableStringSchema,
    sanctions_results: z.array(z.any()).optional().default([]),
    regulatory_results: z.array(z.any()).optional().default([]),
    verdict: NullableStringSchema,
    verdict_rationale: NullableStringSchema,
    llm_summary: NullableStringSchema,
    created_by_agent: NullableStringSchema,
    created_at: FlexibleDateSchema,
  })
  .passthrough();
export type ComplianceAudit = z.infer<typeof ComplianceAuditSchema>;

export const WorkflowRunItemSchema = z
  .object({
    id: z.string(),
    workflow_id: z.string(),
    supplier_id: z.string(),
    workflow_status: WorkflowStatusSchema.optional(),
    status: WorkflowStatusSchema.optional(),
    correlation_id: NullableStringSchema,
    started_at: FlexibleDateSchema,
    completed_at: FlexibleDateSchema,
    error_message: NullableStringSchema,
    final_state_snapshot: z.any().optional().nullable(),
    created_at: FlexibleDateSchema,
    updated_at: FlexibleDateSchema,
  })
  .passthrough();
export type WorkflowRunItem = z.infer<typeof WorkflowRunItemSchema>;

export const TimelineEventSchema = z
  .object({
    id: z.string(),
    workflow_id: z.string(),
    supplier_id: z.string().optional(),
    agent_name: NullableStringSchema,
    event_type: z.string(),
    status: z.string(),
    message: NullableStringSchema,
    payload: NullableRecordSchema,
    error_message: NullableStringSchema,
    created_at: FlexibleDateSchema,
    timestamp: FlexibleDateSchema,
    reasoning_source: NullableStringSchema,
  })
  .passthrough();
export type TimelineEvent = z.infer<typeof TimelineEventSchema>;

export const WorkflowRunResponseSchema = z
  .object({
    success: z.boolean(),
    workflow_id: z.string().optional().nullable(),
    workflow_status: z.string().optional().nullable(),
    supplier_id: z.string(),
    risk_assessment: RiskAssessmentSchema.optional().nullable(),
    anomaly_detection: AnomalyDetectionSchema.optional().nullable(),
    reasoning_summary: NullableStringSchema,
    ai_reasoning_source: NullableStringSchema,
    mitigation_reasoning_summary: NullableStringSchema,
    mitigation_reasoning_source: NullableStringSchema,
    mitigation_plan: MitigationPlanSchema.optional().nullable(),
    execution_record: ExecutionRecordSchema.optional().nullable(),
    execution_reasoning_summary: NullableStringSchema,
    execution_reasoning_source: NullableStringSchema,
    compliance_verdict: NullableStringSchema,
    compliance_reasoning_summary: NullableStringSchema,
    compliance_reasoning_source: NullableStringSchema,
    workflow_complete: NullableBooleanSchema,
  })
  .passthrough();
export type WorkflowRunResponse = z.infer<typeof WorkflowRunResponseSchema>;

export const WorkflowRunsListResponseSchema = z.object({
  success: z.boolean(),
  count: z.number(),
  runs: z.array(WorkflowRunItemSchema),
});
export type WorkflowRunsListResponse = z.infer<typeof WorkflowRunsListResponseSchema>;

export const WorkflowDetailResponseSchema = z.object({
  success: z.boolean(),
  workflow_run: WorkflowRunItemSchema,
});
export type WorkflowDetailResponse = z.infer<typeof WorkflowDetailResponseSchema>;

export const TimelineResponseSchema = z.object({
  success: z.boolean(),
  workflow_id: z.string(),
  count: z.number(),
  timeline: z.array(TimelineEventSchema),
});
export type TimelineResponse = z.infer<typeof TimelineResponseSchema>;

export const ReplayPayloadSchema = z
  .object({
    workflow_run: WorkflowRunItemSchema.optional().nullable(),
    risk_assessment: RiskAssessmentSchema.optional().nullable(),
    mitigation_plan: MitigationPlanSchema.optional().nullable(),
    execution_record: ExecutionRecordSchema.optional().nullable(),
    rfqs: z.array(RFQSchema).optional().default([]),
    compliance_audit: ComplianceAuditSchema.optional().nullable(),
    timeline: z.array(TimelineEventSchema).optional().default([]),
  })
  .passthrough();
export type ReplayPayload = z.infer<typeof ReplayPayloadSchema>;

export const ReplayResponseSchema = z.object({
  success: z.boolean(),
  workflow_id: z.string(),
  replay: ReplayPayloadSchema,
});
export type ReplayResponse = z.infer<typeof ReplayResponseSchema>;

export const AnalyticsSummarySchema = z
  .object({
    total_runs: z.number().optional().default(0),
    completed_runs: z.number().optional().default(0),
    completed_without_mitigation_runs: z.number().optional().default(0),
    failed_runs: z.number().optional().default(0),
    successful_runs: z.number().optional().default(0),
    success_rate: z.number().optional().default(0),
    pending_runs: z.number().optional().default(0),
    avg_risk_score: NullableNumberSchema,
    critical_suppliers: z.number().optional().nullable(),
  })
  .passthrough();
export type AnalyticsSummary = z.infer<typeof AnalyticsSummarySchema>;

export const AnalyticsSummaryResponseSchema = z.object({
  success: z.boolean(),
  summary: AnalyticsSummarySchema,
});
export type AnalyticsSummaryResponse = z.infer<typeof AnalyticsSummaryResponseSchema>;

export const RiskDistributionItemSchema = z
  .object({
    risk_level: RiskLevelSchema,
    count: z.number(),
  })
  .passthrough();
export type RiskDistributionItem = z.infer<typeof RiskDistributionItemSchema>;

export const RiskDistributionResponseSchema = z.object({
  success: z.boolean(),
  distribution: z.array(RiskDistributionItemSchema),
});
export type RiskDistributionResponse = z.infer<typeof RiskDistributionResponseSchema>;

export const SupplierRankingSchema = z
  .object({
    supplier_id: z.string(),
    average_risk_score: z.number().optional(),
    avg_risk_score: z.number().optional(),
    assessment_count: z.number().optional(),
    total_runs: z.number().optional(),
    latest_risk_level: RiskLevelSchema.optional().nullable(),
  })
  .passthrough();
export type SupplierRanking = z.infer<typeof SupplierRankingSchema>;

export const SupplierRankingsResponseSchema = z.object({
  success: z.boolean(),
  rankings: z.array(SupplierRankingSchema),
});
export type SupplierRankingsResponse = z.infer<typeof SupplierRankingsResponseSchema>;
