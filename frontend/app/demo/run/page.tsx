"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Loader2,
  Play,
  Shield,
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
import { apiClient } from "@/lib/api-client";
import type { WorkflowRunResponse } from "@/lib/api-types";

const suppliers = [
  {
    id: "SUP-CN-001",
    name: "China Electronics Manufacturer",
    region: "China",
    category: "Semiconductors",
    exposure: "$1.4M",
    businessRisk: "Port delays and component shortage exposure",
  },
  {
    id: "SUP-DE-001",
    name: "German Auto Parts Supplier",
    region: "Germany",
    category: "Automotive Parts",
    exposure: "$620K",
    businessRisk: "Stable supplier used as backup option",
  },
  {
    id: "SUP-US-001",
    name: "US Tech Components",
    region: "United States",
    category: "Tech Components",
    exposure: "$780K",
    businessRisk: "Shorter lead time but higher unit cost",
  },
  {
    id: "SUP-IN-001",
    name: "Indian Semiconductor Supplier",
    region: "India",
    category: "Semiconductors",
    exposure: "$510K",
    businessRisk: "Lead-time anomaly under observation",
  },
  {
    id: "SUP-IR-001",
    name: "Iran Raw Materials",
    region: "Iran",
    category: "Raw Materials",
    exposure: "$420K",
    businessRisk: "Compliance and trade-control review required",
  },
];

const quickPrompts = [
  "Why is this supplier risky?",
  "Find safer alternatives.",
  "Generate a mitigation plan.",
  "Create RFQ recommendations.",
  "Check compliance exposure.",
];

const progressStages = [
  "Understanding investigation request",
  "Risk Analyst assessing supplier exposure",
  "Mitigation Strategist comparing alternatives",
  "Execution Agent preparing RFQ actions",
  "Compliance Agent reviewing policy constraints",
];

function inferSupplierFromPrompt(prompt: string) {
  const upper = prompt.toUpperCase();

  const explicitSupplier = suppliers.find((supplier) =>
    upper.includes(supplier.id)
  );

  if (explicitSupplier) {
    return explicitSupplier.id;
  }

  if (upper.includes("CHINA") || upper.includes("SEMICONDUCTOR")) {
    return "SUP-CN-001";
  }

  if (upper.includes("GERMAN") || upper.includes("GERMANY")) {
    return "SUP-DE-001";
  }

  if (upper.includes("US ") || upper.includes("UNITED STATES")) {
    return "SUP-US-001";
  }

  if (upper.includes("INDIA") || upper.includes("INDIAN")) {
    return "SUP-IN-001";
  }

  if (upper.includes("IRAN") || upper.includes("COMPLIANCE")) {
    return "SUP-IR-001";
  }

  return null;
}

function inferIntent(prompt: string) {
  const lower = prompt.toLowerCase();

  if (lower.includes("rfq") || lower.includes("quote")) {
    return "RFQ generation";
  }

  if (lower.includes("compliance") || lower.includes("sanction") || lower.includes("trade")) {
    return "Compliance review";
  }

  if (lower.includes("alternative") || lower.includes("safer") || lower.includes("backup")) {
    return "Supplier alternatives";
  }

  if (lower.includes("mitigation") || lower.includes("plan")) {
    return "Mitigation planning";
  }

  if (lower.includes("why") || lower.includes("risk")) {
    return "Risk explanation";
  }

  return "General investigation";
}

function getInvestigationSummary(result: WorkflowRunResponse | null) {
  if (!result) {
    return null;
  }

  const riskLevel = result.risk_assessment?.level ?? "UNKNOWN";
  const riskScore = result.risk_assessment?.score ?? "N/A";
  const hasMitigation = Boolean(result.mitigation_plan);
  const hasExecution = Boolean(result.execution_record);
  const verdict = result.compliance_verdict ?? "Pending review";

  return {
    riskLevel,
    riskScore,
    recommendedAction: hasMitigation
      ? "Review the generated mitigation plan and approve the best supplier/RFQ option."
      : "Continue monitoring. No mitigation plan was required by the workflow.",
    executionStatus: hasExecution
      ? "RFQ or execution record was generated."
      : "No RFQ execution was generated.",
    complianceStatus: verdict,
  };
}

export default function DemoRunPage() {
  const [selectedSupplier, setSelectedSupplier] = useState(suppliers[0].id);
  const [result, setResult] = useState<WorkflowRunResponse | null>(null);
  const [promptText, setPromptText] = useState(
    "Investigate SUP-CN-001 supplier risk and recommend the best mitigation action."
  );
  const [activeStage, setActiveStage] = useState(0);

  const runWorkflowMutation = useMutation({
    mutationFn: (supplierId: string) => apiClient.runWorkflow(supplierId),
    onSuccess: setResult,
  });

  const selected = suppliers.find((supplier) => supplier.id === selectedSupplier);
  const investigationSummary = useMemo(() => getInvestigationSummary(result), [result]);
  const detectedIntent = useMemo(() => inferIntent(promptText), [promptText]);

  useEffect(() => {
    const inferredSupplier = inferSupplierFromPrompt(promptText);

    if (inferredSupplier && inferredSupplier !== selectedSupplier) {
      setSelectedSupplier(inferredSupplier);
    }
  }, [promptText, selectedSupplier]);

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
    const inferredSupplier = inferSupplierFromPrompt(promptText);
    const supplierToRun = inferredSupplier ?? selectedSupplier;

    setSelectedSupplier(supplierToRun);
    setResult(null);
    setActiveStage(0);
    runWorkflowMutation.mutate(supplierToRun);
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-950">
            AI Investigation Center
          </h1>
          <p className="mt-2 max-w-3xl text-slate-600">
            Ask a supply chain question, select the affected supplier, and let
            the agent workflow assess risk, mitigation, RFQ actions, and
            compliance exposure.
          </p>
        </div>

        <div className="rounded-lg border border-violet-200 bg-violet-50 px-4 py-3 text-sm font-semibold text-violet-900">
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            AMD ROCm + vLLM
          </div>
          <div className="mt-1 text-xs font-normal text-violet-700">
            Shown where agent inference uses amd_vllm.
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Ask SupplyChain Guardian</CardTitle>
          <CardDescription>
            The assistant detects supplier context and investigation intent,
            then runs the workflow against the selected supplier.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <textarea
            value={promptText}
            onChange={(event) => setPromptText(event.target.value)}
            className="min-h-28 w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-slate-400"
            placeholder="Example: Find safer alternatives for SUP-CN-001 and explain the operational impact."
          />

          <div className="flex flex-wrap gap-2">
            {quickPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => setPromptText(prompt)}
                className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:border-slate-300 hover:bg-slate-50"
              >
                {prompt}
              </button>
            ))}
          </div>

          <div className="grid gap-3 rounded-lg border bg-slate-50 p-4 md:grid-cols-3">
            <div>
              <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Detected intent
              </div>
              <div className="mt-1 font-semibold text-slate-950">
                {detectedIntent}
              </div>
            </div>

            <div>
              <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Supplier context
              </div>
              <div className="mt-1 font-semibold text-slate-950">
                {selectedSupplier}
              </div>
            </div>

            <div>
              <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Next action
              </div>
              <div className="mt-1 text-sm text-slate-700">
                Run agent investigation
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Select Operational Context</CardTitle>
          <CardDescription>
            Choose the supplier or disruption source that the AI agents should
            investigate.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
            {suppliers.map((supplier) => (
              <button
                key={supplier.id}
                type="button"
                onClick={() => setSelectedSupplier(supplier.id)}
                className={`rounded-lg border p-4 text-left transition ${
                  selectedSupplier === supplier.id
                    ? "border-slate-900 bg-slate-950 text-white shadow-sm"
                    : "border-slate-200 bg-white hover:border-slate-400"
                }`}
              >
                <div className="font-semibold">{supplier.id}</div>

                <div
                  className={`mt-1 text-sm ${
                    selectedSupplier === supplier.id
                      ? "text-slate-200"
                      : "text-slate-600"
                  }`}
                >
                  {supplier.name}
                </div>

                <div
                  className={`mt-3 text-xs ${
                    selectedSupplier === supplier.id
                      ? "text-slate-300"
                      : "text-slate-500"
                  }`}
                >
                  {supplier.region} • {supplier.category}
                </div>
              </button>
            ))}
          </div>

          {selected ? (
            <div className="grid gap-3 rounded-lg border bg-slate-50 p-4 md:grid-cols-3">
              <div>
                <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Selected supplier
                </div>
                <div className="mt-1 font-semibold text-slate-950">
                  {selected.name}
                </div>
              </div>

              <div>
                <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Estimated exposure
                </div>
                <div className="mt-1 font-semibold text-slate-950">
                  {selected.exposure}
                </div>
              </div>

              <div>
                <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Business context
                </div>
                <div className="mt-1 text-sm text-slate-700">
                  {selected.businessRisk}
                </div>
              </div>
            </div>
          ) : null}

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm text-muted-foreground">
              The agents will assess risk, mitigation, RFQ execution, and
              compliance status.
            </div>

            <Button
              onClick={startInvestigation}
              disabled={runWorkflowMutation.isPending}
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
            <CardTitle>Agent Progress</CardTitle>
            <CardDescription>
              Progress is simulated on the client until the backend returns the
              final workflow result.
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
                    className={`flex h-8 w-8 items-center justify-center rounded-full ${
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
                      {isDone ? "Completed" : isActive ? "Running" : "Waiting"}
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
            <AlertCircle className="mt-0.5 h-5 w-5 text-red-700" />
            <div>
              <div className="font-semibold text-red-950">Investigation failed</div>
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
                <CheckCircle2 className="mt-0.5 h-6 w-6 text-emerald-700" />
                <div>
                  <div className="font-semibold text-emerald-950">
                    Investigation {result.workflow_status ?? "completed"}
                  </div>
                  <div className="text-sm text-emerald-800">
                    {result.workflow_id
                      ? `Workflow ID ${result.workflow_id}`
                      : "Workflow ID not returned"}
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
                <CardTitle>Operational Decision Summary</CardTitle>
                <CardDescription>
                  Business-facing interpretation of the agent workflow result.
                </CardDescription>
              </CardHeader>

              <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <SummaryTile label="Risk level" value={String(investigationSummary.riskLevel)} />
                <SummaryTile label="Risk score" value={String(investigationSummary.riskScore)} />
                <SummaryTile label="Execution" value={investigationSummary.executionStatus} />
                <SummaryTile label="Compliance" value={String(investigationSummary.complianceStatus)} />

                <div className="rounded-lg border bg-emerald-50 p-4 md:col-span-2 xl:col-span-4">
                  <div className="flex items-start gap-3">
                    <Sparkles className="mt-0.5 h-5 w-5 text-emerald-700" />

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

function SummaryTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </div>
      <div className="mt-2 text-sm font-semibold text-slate-950">{value}</div>
    </div>
  );
}