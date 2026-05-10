"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Loader2,
  Play,
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
import {
  ComplianceCard,
  ExecutionRecordCard,
  MitigationPlanCard,
  ReasoningBadgeRow,
  RiskAssessmentCard,
  WorkflowMetadataCard,
} from "@/components/workflow/workflow-sections";
import {
  detectChatIntent,
  detectSupplierId,
  getIntentNextAction,
  investigationPrompts,
} from "@/lib/chat-intents";
import { apiClient } from "@/lib/api-client";
import type { WorkflowRunResponse } from "@/lib/api-types";
import { getSupplierProfile, supplierProfiles } from "@/lib/operational-data";
import { normalizeRiskAssessment } from "@/lib/workflow-normalizers";

const progressStages = [
  "Understanding request",
  "Risk analysis",
  "Mitigation planning",
  "RFQ preparation",
  "Compliance review",
];

function getInvestigationSummary(result: WorkflowRunResponse | null) {
  if (!result) {
    return null;
  }

  const risk = normalizeRiskAssessment(result.risk_assessment);
  const hasMitigation = Boolean(result.mitigation_plan);
  const hasExecution = Boolean(result.execution_record);

  return {
    riskLevel: risk?.level ?? "UNKNOWN",
    riskScore: risk?.scoreLabel ?? "N/A",
    recommendedAction: hasMitigation
      ? "Review the mitigation plan and approve the best supplier/RFQ option."
      : risk?.recommendation ?? "Continue monitoring. No mitigation was required.",
    executionStatus: hasExecution
      ? "RFQ generated or execution record created."
      : "No RFQ execution was generated.",
    complianceStatus: result.compliance_verdict ?? "Pending review",
  };
}

export function InvestigationAssistant() {
  const [selectedSupplier, setSelectedSupplier] = useState(supplierProfiles[0].id);
  const [result, setResult] = useState<WorkflowRunResponse | null>(null);
  const [promptText, setPromptText] = useState(
    "Investigate SUP-CN-001 and recommend mitigation."
  );
  const [activeStage, setActiveStage] = useState(0);

  const runWorkflowMutation = useMutation({
    mutationFn: (supplierId: string) => apiClient.runWorkflow(supplierId),
    onSuccess: setResult,
  });

  const selected = getSupplierProfile(selectedSupplier);
  const detectedIntent = useMemo(() => detectChatIntent(promptText), [promptText]);
  const detectedSupplier = useMemo(() => detectSupplierId(promptText), [promptText]);
  const investigationSummary = useMemo(
    () => getInvestigationSummary(result),
    [result]
  );

  useEffect(() => {
    if (detectedSupplier && detectedSupplier !== selectedSupplier) {
      setSelectedSupplier(detectedSupplier);
    }
  }, [detectedSupplier, selectedSupplier]);

  useEffect(() => {
    if (!runWorkflowMutation.isPending) {
      setActiveStage(0);
      return;
    }

    const interval = window.setInterval(() => {
      setActiveStage((current) =>
        current >= progressStages.length - 1 ? current : current + 1
      );
    }, 1200);

    return () => window.clearInterval(interval);
  }, [runWorkflowMutation.isPending]);

  function startInvestigation() {
    const supplierToRun = detectedSupplier ?? selectedSupplier;

    setSelectedSupplier(supplierToRun);
    setResult(null);
    setActiveStage(0);
    runWorkflowMutation.mutate(supplierToRun);
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Ask SupplyChain Guardian</CardTitle>
          <CardDescription>
            Describe the supplier issue. The assistant detects intent and
            supplier context before running the agent workflow.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Your question
            </label>
            <textarea
              value={promptText}
              onChange={(event) => setPromptText(event.target.value)}
              placeholder="Example: Why is SUP-CN-001 risky? Find safer alternatives."
              className="min-h-[104px] w-full rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-slate-400 disabled:bg-slate-50"
              disabled={runWorkflowMutation.isPending}
            />
          </div>

          <div className="flex flex-wrap gap-2">
            {investigationPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => setPromptText(prompt)}
                disabled={runWorkflowMutation.isPending}
                className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {prompt}
              </button>
            ))}
          </div>

          <div className="grid gap-3 rounded-lg border bg-slate-50 p-4 md:grid-cols-3">
            <ContextTile label="Detected intent" value={detectedIntent} />
            <ContextTile label="Supplier context" value={selected.id} />
            <ContextTile
              label="Next action"
              value={getIntentNextAction(detectedIntent)}
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Supplier to investigate
            </label>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
              {supplierProfiles.map((supplier) => (
                <button
                  key={supplier.id}
                  type="button"
                  onClick={() => setSelectedSupplier(supplier.id)}
                  disabled={runWorkflowMutation.isPending}
                  className={`rounded-lg border p-3 text-left text-sm transition disabled:cursor-not-allowed disabled:opacity-60 ${
                    selectedSupplier === supplier.id
                      ? "border-slate-900 bg-slate-950 text-white"
                      : "border-slate-200 bg-white hover:border-slate-300"
                  }`}
                >
                  <div className="font-semibold">{supplier.id}</div>
                  <div
                    className={`mt-1 text-xs ${
                      selectedSupplier === supplier.id
                        ? "text-slate-300"
                        : "text-slate-500"
                    }`}
                  >
                    {supplier.name}
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="grid gap-3 rounded-lg border bg-white p-4 md:grid-cols-3">
            <ContextTile label="Estimated exposure" value={selected.exposure} />
            <ContextTile label="Risk context" value={selected.businessRisk} />
            <ContextTile
              label="Recommended action"
              value={selected.recommendedAction}
            />
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm text-slate-600">
              The workflow checks risk, mitigation, RFQ readiness, and compliance.
            </div>

            <Button
              onClick={startInvestigation}
              disabled={runWorkflowMutation.isPending || !promptText.trim()}
              size="lg"
            >
              {runWorkflowMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Investigating
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  Run Investigation
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {runWorkflowMutation.isPending ? (
        <Card>
          <CardHeader>
            <CardTitle>Investigation Progress</CardTitle>
            <CardDescription>
              Agent progress is shown while the backend workflow runs.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-3">
            {progressStages.map((stage, index) => {
              const isDone = index < activeStage;
              const isActive = index === activeStage;

              return (
                <div
                  key={stage}
                  className="flex items-center gap-3 rounded-lg border bg-white p-3"
                >
                  <div
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                      isDone
                        ? "bg-emerald-50 text-emerald-700"
                        : isActive
                          ? "bg-blue-50 text-blue-700"
                          : "bg-slate-100 text-slate-400"
                    }`}
                  >
                    {isDone ? (
                      <CheckCircle2 className="h-4 w-4" />
                    ) : isActive ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Clock className="h-4 w-4" />
                    )}
                  </div>

                  <div>
                    <div className="font-medium text-slate-950">{stage}</div>
                    <div className="text-xs text-slate-500">
                      {isDone ? "Complete" : isActive ? "Running" : "Waiting"}
                    </div>
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>
      ) : null}

      {runWorkflowMutation.isError ? (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="flex items-start gap-3 pt-6">
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-700" />
            <div>
              <div className="font-semibold text-red-950">
                Investigation failed
              </div>
              <p className="mt-1 text-sm text-red-800">
                {runWorkflowMutation.error instanceof Error
                  ? runWorkflowMutation.error.message
                  : "Unknown backend error"}
              </p>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {result ? (
        <div className="space-y-6">
          <Card className="border-emerald-200 bg-emerald-50">
            <CardContent className="flex flex-col gap-4 pt-6 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="mt-0.5 h-6 w-6 shrink-0 text-emerald-700" />
                <div>
                  <div className="font-semibold text-emerald-950">
                    Investigation complete
                  </div>
                  <div className="break-all text-sm text-emerald-800">
                    Workflow {result.workflow_id ?? "completed"}
                  </div>
                </div>
              </div>

              <ReasoningBadgeRow
                sources={{
                  ai: result.ai_reasoning_source,
                  mitigation: result.mitigation_reasoning_source,
                  execution: result.execution_reasoning_source,
                  compliance: result.compliance_reasoning_source,
                }}
              />
            </CardContent>
          </Card>

          {investigationSummary ? (
            <Card>
              <CardHeader>
                <CardTitle>Decision Summary</CardTitle>
                <CardDescription>
                  The operational answer from this investigation.
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  <SummaryTile
                    label="Risk level"
                    value={String(investigationSummary.riskLevel)}
                  />
                  <SummaryTile
                    label="Risk score"
                    value={String(investigationSummary.riskScore)}
                  />
                  <SummaryTile
                    label="Execution"
                    value={investigationSummary.executionStatus}
                  />
                  <SummaryTile
                    label="Compliance"
                    value={String(investigationSummary.complianceStatus)}
                  />
                </div>

                <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
                  <div className="flex items-start gap-3">
                    <Sparkles className="mt-0.5 h-5 w-5 shrink-0 text-emerald-700" />
                    <div>
                      <div className="font-semibold text-emerald-950">
                        Recommended next action
                      </div>
                      <p className="mt-1 text-sm text-emerald-800">
                        {investigationSummary.recommendedAction}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : null}

          <WorkflowMetadataCard
            workflowId={result.workflow_id}
            supplierId={result.supplier_id}
            status={result.workflow_status}
          />

          <RiskAssessmentCard
            risk={result.risk_assessment}
            anomaly={result.anomaly_detection}
            reasoning={result.reasoning_summary}
            source={result.ai_reasoning_source}
          />

          <MitigationPlanCard
            plan={result.mitigation_plan}
            reasoning={result.mitigation_reasoning_summary}
            source={result.mitigation_reasoning_source}
          />

          <ExecutionRecordCard
            execution={result.execution_record}
            reasoning={result.execution_reasoning_summary}
            source={result.execution_reasoning_source}
          />

          <ComplianceCard
            verdict={result.compliance_verdict}
            reasoning={result.compliance_reasoning_summary}
            source={result.compliance_reasoning_source}
          />
        </div>
      ) : null}
    </div>
  );
}

function ContextTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </div>
      <div className="mt-1 break-words text-sm font-semibold text-slate-950">
        {value}
      </div>
    </div>
  );
}

function SummaryTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </div>
      <div className="mt-2 break-words text-sm font-semibold text-slate-950">
        {value}
      </div>
    </div>
  );
}
