"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Clock3,
  Filter,
  Loader2,
  RadioTower,
  Search,
  ShieldCheck,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api-client";

type RFQStatus =
  | "Pending Approval"
  | "Draft"
  | "Approved"
  | "Compliance Review";

type RFQRecord = {
  supplier: string;
  alternateSupplier: string;
  price: string;
  leadTime: string;
  risk: string;
  status: RFQStatus;
  reason: string;
};

const mockStatuses: RFQStatus[] = [
  "Pending Approval",
  "Draft",
  "Approved",
  "Compliance Review",
];

function deriveRFQsFromReplay(data: unknown): RFQRecord[] {
  if (!data || typeof data !== "object") {
    return [];
  }

  const replay = data as Record<string, unknown>;
  const supplierId =
    typeof replay.supplier_id === "string"
      ? replay.supplier_id
      : "UNKNOWN-SUPPLIER";

  const mitigation =
    replay.mitigation_plan && typeof replay.mitigation_plan === "object"
      ? (replay.mitigation_plan as Record<string, unknown>)
      : null;

  const options = Array.isArray(mitigation?.recommended_options)
    ? mitigation?.recommended_options
    : [];

  if (!options.length) {
    return [];
  }

  return options.map((option, index) => {
    const item =
      option && typeof option === "object"
        ? (option as Record<string, unknown>)
        : {};

    return {
      supplier: supplierId,
      alternateSupplier:
        typeof item.supplier_id === "string"
          ? item.supplier_id
          : `ALT-SUP-${index + 1}`,
      price:
        typeof item.estimated_cost === "string"
          ? item.estimated_cost
          : `$${(index + 1) * 12000}`,
      leadTime:
        typeof item.lead_time === "string"
          ? item.lead_time
          : `${4 + index} days`,
      risk:
        typeof item.risk_level === "string"
          ? item.risk_level
          : "LOW",
      status:
        mockStatuses[index % mockStatuses.length] ?? "Pending Approval",
      reason:
        typeof item.reason === "string"
          ? item.reason
          : "AI-generated mitigation recommendation.",
    };
  });
}

export default function RFQsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<RFQStatus | "All">("All");

  const workflowsQuery = useQuery({
    queryKey: ["workflow-runs-rfqs"],
    queryFn: async () => {
      const runs = await apiClient.listWorkflowRuns(10);

      const replayResults = await Promise.all(
        runs.runs.map(async (run) => {
          try {
            return await apiClient.getWorkflowReplay(run.workflow_id);
          } catch {
            return null;
          }
        })
      );

      return replayResults.filter(Boolean);
    },
  });

  const rfqs = useMemo(() => {
    return workflowsQuery.data?.flatMap((replay) =>
      deriveRFQsFromReplay(replay)
    ) ?? [];
  }, [workflowsQuery.data]);

  const filtered = rfqs.filter((rfq) => {
    const matchesSearch =
      rfq.supplier.toLowerCase().includes(search.toLowerCase()) ||
      rfq.alternateSupplier
        .toLowerCase()
        .includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === "All" || rfq.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-950">
            RFQ Command Center
          </h1>
          <p className="mt-2 max-w-3xl text-slate-600">
            Review AI-generated sourcing recommendations, compare alternate
            suppliers, and manage approval decisions before execution.
          </p>
        </div>

        <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm">
          <div className="font-semibold text-blue-900">
            Procurement Operations
          </div>
          <div className="mt-1 text-blue-700">
            RFQs are currently derived from workflow replay data until a
            dedicated backend RFQ endpoint is implemented.
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <OverviewCard
          title="Pending Approval"
          value="5"
          detail="Waiting for procurement review"
          icon={Clock3}
        />
        <OverviewCard
          title="Approved"
          value="8"
          detail="Ready for supplier engagement"
          icon={CheckCircle2}
        />
        <OverviewCard
          title="Compliance Review"
          value="2"
          detail="Need regulatory clearance"
          icon={ShieldCheck}
        />
        <OverviewCard
          title="Total RFQs"
          value={rfqs.length}
          detail="Generated from mitigation workflows"
          icon={RadioTower}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filter RFQs</CardTitle>
          <CardDescription>
            Search by supplier or narrow by operational status.
          </CardDescription>
        </CardHeader>

        <CardContent className="grid gap-4 md:grid-cols-2">
          <div className="relative">
            <Search className="absolute left-3 top-3.5 h-4 w-4 text-slate-400" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search supplier or alternate supplier"
              className="h-11 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-4 text-sm outline-none transition focus:border-slate-400"
            />
          </div>

          <div className="relative">
            <Filter className="absolute left-3 top-3.5 h-4 w-4 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(event.target.value as RFQStatus | "All")
              }
              className="h-11 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-4 text-sm outline-none transition focus:border-slate-400"
            >
              <option value="All">All statuses</option>
              {mockStatuses.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Supplier RFQ Recommendations</CardTitle>
          <CardDescription>
            Compare alternate suppliers, pricing, lead time, and operational
            risk before approving sourcing decisions.
          </CardDescription>
        </CardHeader>

        <CardContent>
          {workflowsQuery.isLoading ? (
            <div className="flex items-center gap-2 py-8 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading RFQ recommendations
            </div>
          ) : workflowsQuery.isError ? (
            <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4">
              <AlertCircle className="mt-0.5 h-5 w-5 text-red-700" />
              <div>
                <div className="font-semibold text-red-950">
                  Failed to load RFQs
                </div>
                <p className="mt-1 text-sm text-red-800">
                  {workflowsQuery.error instanceof Error
                    ? workflowsQuery.error.message
                    : "Unknown backend error"}
                </p>
              </div>
            </div>
          ) : filtered.length ? (
            <div className="space-y-4">
              {filtered.map((rfq, index) => (
                <div
                  key={`${rfq.supplier}-${rfq.alternateSupplier}-${index}`}
                  className="rounded-xl border bg-white p-5"
                >
                  <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <div className="font-semibold text-slate-950">
                          {rfq.supplier}
                        </div>

                        <ArrowRight className="h-4 w-4 text-slate-400" />

                        <div className="font-semibold text-slate-950">
                          {rfq.alternateSupplier}
                        </div>

                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                            rfq.status === "Pending Approval"
                              ? "bg-orange-50 text-orange-700"
                              : rfq.status === "Approved"
                                ? "bg-emerald-50 text-emerald-700"
                                : rfq.status === "Compliance Review"
                                  ? "bg-red-50 text-red-700"
                                  : "bg-slate-100 text-slate-700"
                          }`}
                        >
                          {rfq.status}
                        </span>
                      </div>

                      <div className="mt-3 grid gap-3 md:grid-cols-3">
                        <DataTile
                          label="Estimated Price"
                          value={rfq.price}
                        />
                        <DataTile
                          label="Lead Time"
                          value={rfq.leadTime}
                        />
                        <DataTile
                          label="Risk"
                          value={rfq.risk}
                        />
                      </div>

                      <div className="mt-4 rounded-lg bg-slate-50 p-3">
                        <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
                          AI Recommendation
                        </div>
                        <div className="mt-1 text-sm text-slate-700">
                          {rfq.reason}
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-col gap-2">
                      <Button>
                        Approve RFQ
                      </Button>

                      <Button variant="outline">
                        Request Review
                      </Button>

                      <Button variant="outline">
                        Reject
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-lg border border-dashed p-8 text-center">
              <div className="font-semibold text-slate-950">
                No RFQs found
              </div>
              <p className="mt-1 text-sm text-muted-foreground">
                Run mitigation workflows to generate supplier recommendations.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function OverviewCard({
  title,
  value,
  detail,
  icon: Icon,
}: {
  title: string;
  value: string | number;
  detail: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <Card>
      <CardContent className="flex items-start justify-between gap-3 p-5">
        <div>
          <div className="text-sm font-medium text-slate-500">
            {title}
          </div>
          <div className="mt-2 text-3xl font-bold text-slate-950">
            {value}
          </div>
          <div className="mt-1 text-xs text-slate-500">
            {detail}
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-slate-50 p-2 text-slate-600">
          <Icon className="h-4 w-4" />
        </div>
      </CardContent>
    </Card>
  );
}

function DataTile({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border bg-white p-3">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </div>
      <div className="mt-1 font-semibold text-slate-950">
        {value}
      </div>
    </div>
  );
}