"use client";

import { useMemo, useState } from "react";
import type { ComponentType } from "react";
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

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { apiClient } from "@/lib/api-client";
import type { ReplayResponse } from "@/lib/api-types";
import {
  normalizeWorkflowReplay,
  type NormalizedRFQ,
} from "@/lib/workflow-normalizers";

type RFQStatus = NormalizedRFQ["status"];
type StatusFilter = RFQStatus | "All";

const statusOptions: StatusFilter[] = [
  "All",
  "Pending Approval",
  "Approved",
  "Compliance Review",
  "Draft",
  "Rejected",
];

function isReplayResponse(value: ReplayResponse | null): value is ReplayResponse {
  return Boolean(value);
}

function getStatusClass(status: RFQStatus) {
  switch (status) {
    case "Pending Approval":
      return "bg-orange-50 text-orange-700";
    case "Approved":
      return "bg-emerald-50 text-emerald-700";
    case "Compliance Review":
      return "bg-red-50 text-red-700";
    case "Rejected":
      return "bg-slate-200 text-slate-700";
    default:
      return "bg-slate-100 text-slate-700";
  }
}

export default function RFQsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("All");
  const [localStatuses, setLocalStatuses] = useState<Record<string, RFQStatus>>({});

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

      return replayResults.filter(isReplayResponse);
    },
  });

  const rfqs = useMemo(() => {
    const normalized =
      workflowsQuery.data?.flatMap((replay) =>
        normalizeWorkflowReplay(replay.replay, replay.workflow_id).rfqs
      ) ?? [];

    return normalized.map((rfq) => ({
      ...rfq,
      status: localStatuses[rfq.id] ?? rfq.status,
    }));
  }, [localStatuses, workflowsQuery.data]);

  const filtered = rfqs.filter((rfq) => {
    const query = search.toLowerCase();
    const matchesSearch =
      rfq.supplierId.toLowerCase().includes(query) ||
      rfq.supplierName.toLowerCase().includes(query) ||
      rfq.originalSupplierId?.toLowerCase().includes(query) ||
      rfq.id.toLowerCase().includes(query);

    const matchesStatus =
      statusFilter === "All" || rfq.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const counts = {
    pending: rfqs.filter((rfq) => rfq.status === "Pending Approval").length,
    approved: rfqs.filter((rfq) => rfq.status === "Approved").length,
    compliance: rfqs.filter((rfq) => rfq.status === "Compliance Review").length,
    total: rfqs.length,
  };

  function updateLocalStatus(id: string, status: RFQStatus) {
    setLocalStatuses((current) => ({ ...current, [id]: status }));
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-950">
            RFQ Decision Center
          </h1>
          <p className="mt-2 max-w-3xl text-slate-600">
            Compare alternate suppliers, review approval blockers, and decide
            which sourcing action should move forward.
          </p>
        </div>

        <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm">
          <div className="font-semibold text-blue-900">Review-only actions</div>
          <div className="mt-1 text-blue-700">
            Approval controls update this browser session only. Backend
            persistence is not connected yet.
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <OverviewCard
          title="Pending Approval"
          value={counts.pending}
          detail="Need procurement decision"
          icon={Clock3}
        />
        <OverviewCard
          title="Approved"
          value={counts.approved}
          detail="Marked ready in review"
          icon={CheckCircle2}
        />
        <OverviewCard
          title="Compliance Review"
          value={counts.compliance}
          detail="Need policy clearance"
          icon={ShieldCheck}
        />
        <OverviewCard
          title="Total RFQs"
          value={counts.total}
          detail="From recent workflows"
          icon={RadioTower}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Find RFQs</CardTitle>
          <CardDescription>
            Search by supplier, RFQ ID, or original supplier and filter by review status.
          </CardDescription>
        </CardHeader>

        <CardContent className="grid gap-4 md:grid-cols-2">
          <div className="relative">
            <Search className="absolute left-3 top-3.5 h-4 w-4 text-slate-400" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search supplier, RFQ, or workflow context"
              className="h-11 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-4 text-sm outline-none transition focus:border-slate-400"
            />
          </div>

          <div className="relative">
            <Filter className="absolute left-3 top-3.5 h-4 w-4 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value as StatusFilter)}
              className="h-11 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-4 text-sm outline-none transition focus:border-slate-400"
            >
              {statusOptions.map((status) => (
                <option key={status} value={status}>
                  {status === "All" ? "All statuses" : status}
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
            Compare price, lead time, risk, and AI rationale before acting.
          </CardDescription>
        </CardHeader>

        <CardContent>
          {workflowsQuery.isLoading ? (
            <div className="flex items-center gap-2 py-8 text-sm text-slate-600">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading RFQ recommendations
            </div>
          ) : workflowsQuery.isError ? (
            <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-700" />
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
              {filtered.map((rfq) => (
                <div key={rfq.id} className="rounded-lg border bg-white p-5">
                  <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <div className="break-all font-semibold text-slate-950">
                          {rfq.originalSupplierId ?? "Original supplier"}
                        </div>
                        <ArrowRight className="h-4 w-4 text-slate-400" />
                        <div className="break-all font-semibold text-slate-950">
                          {rfq.supplierName}
                        </div>
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-semibold ${getStatusClass(
                            rfq.status
                          )}`}
                        >
                          {rfq.status}
                        </span>
                      </div>

                      <div className="mt-1 break-all font-mono text-xs text-slate-400">
                        RFQ {rfq.id}
                      </div>

                      <div className="mt-3 grid gap-3 md:grid-cols-3">
                        <DataTile label="Price" value={rfq.price} />
                        <DataTile label="Lead Time" value={rfq.leadTime} />
                        <DataTile label="Risk" value={rfq.risk} />
                      </div>

                      <div className="mt-4 rounded-lg bg-slate-50 p-3">
                        <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
                          Why this matters
                        </div>
                        <div className="mt-1 text-sm text-slate-700">
                          {rfq.reason}
                        </div>
                      </div>
                    </div>

                    <div className="flex w-full flex-col gap-2 xl:w-44">
                      <Button
                        onClick={() => updateLocalStatus(rfq.id, "Approved")}
                        disabled={rfq.status === "Approved"}
                      >
                        Approve RFQ
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() =>
                          updateLocalStatus(rfq.id, "Compliance Review")
                        }
                        disabled={rfq.status === "Compliance Review"}
                      >
                        Request Review
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => updateLocalStatus(rfq.id, "Rejected")}
                        disabled={rfq.status === "Rejected"}
                      >
                        Reject
                      </Button>
                      <div className="text-xs leading-5 text-slate-500">
                        Local review state only. Not persisted.
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-lg border border-dashed p-8 text-center">
              <div className="font-semibold text-slate-950">No RFQs found</div>
              <p className="mt-1 text-sm text-slate-600">
                Run mitigation workflows or clear filters to see recommendations.
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
  icon: ComponentType<{ className?: string }>;
}) {
  return (
    <Card>
      <CardContent className="flex items-start justify-between gap-3 p-5">
        <div>
          <div className="text-sm font-medium text-slate-500">{title}</div>
          <div className="mt-2 text-3xl font-bold text-slate-950">{value}</div>
          <div className="mt-1 text-xs text-slate-500">{detail}</div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-slate-50 p-2 text-slate-600">
          <Icon className="h-4 w-4" />
        </div>
      </CardContent>
    </Card>
  );
}

function DataTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 rounded-lg border bg-white p-3">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </div>
      <div className="mt-1 break-words font-semibold text-slate-950">
        {value}
      </div>
    </div>
  );
}
