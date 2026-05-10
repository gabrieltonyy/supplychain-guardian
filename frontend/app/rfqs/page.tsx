"use client";

import { useMemo, useState } from "react";
import type { ComponentType } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  CheckCircle2,
  Clock3,
  Filter,
  Loader2,
  RadioTower,
  RefreshCcw,
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
import type { RFQ } from "@/lib/api-types";
import { formatCurrency, formatDate, getRfqTargetPrice, normalizeStatus } from "@/lib/utils";

type RFQReviewStatus =
  | "ALL"
  | "DRAFT"
  | "PENDING_APPROVAL"
  | "APPROVED"
  | "REVIEW_REQUESTED"
  | "REJECTED"
  | "COMPLIANCE_REVIEW";

type RFQAction = "approve" | "request-review" | "reject";

const statusOptions: Array<{ value: RFQReviewStatus; label: string }> = [
  { value: "ALL", label: "All statuses" },
  { value: "PENDING_APPROVAL", label: "Pending Approval" },
  { value: "APPROVED", label: "Approved" },
  { value: "REVIEW_REQUESTED", label: "Review Requested" },
  { value: "COMPLIANCE_REVIEW", label: "Compliance Review" },
  { value: "DRAFT", label: "Draft" },
  { value: "REJECTED", label: "Rejected" },
];

function getStatusClass(status?: string | null) {
  switch (status) {
    case "PENDING_APPROVAL":
      return "bg-orange-50 text-orange-700";
    case "APPROVED":
      return "bg-emerald-50 text-emerald-700";
    case "COMPLIANCE_REVIEW":
    case "REVIEW_REQUESTED":
      return "bg-red-50 text-red-700";
    case "REJECTED":
      return "bg-slate-200 text-slate-700";
    default:
      return "bg-slate-100 text-slate-700";
  }
}

export default function RFQsPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<RFQReviewStatus>("ALL");
  const [mutatingId, setMutatingId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{ tone: "success" | "error"; message: string } | null>(null);

  const allRfqsQuery = useQuery({
    queryKey: ["rfqs", "all-counts"],
    queryFn: () => apiClient.listRFQs({ limit: 200 }),
  });

  const rfqsQuery = useQuery({
    queryKey: ["rfqs", search, statusFilter],
    queryFn: () =>
      apiClient.listRFQs({
        search: search.trim() || undefined,
        status: statusFilter,
        limit: 100,
      }),
  });

  const actionMutation = useMutation({
    mutationFn: async ({ rfqId, action }: { rfqId: string; action: RFQAction }) => {
      setMutatingId(rfqId);

      if (action === "approve") {
        return apiClient.approveRFQ(rfqId, "Approved from RFQ Decision Center");
      }

      if (action === "request-review") {
        return apiClient.requestRFQReview(rfqId, "Review requested from RFQ Decision Center");
      }

      return apiClient.rejectRFQ(rfqId, "Rejected from RFQ Decision Center");
    },
    onSuccess: async (response) => {
      setFeedback({
        tone: "success",
        message: `${response.rfq.rfq_id} updated to ${statusLabel(response.rfq.status)}.`,
      });
      await queryClient.invalidateQueries({ queryKey: ["rfqs"] });
    },
    onError: (error) => {
      setFeedback({
        tone: "error",
        message: error instanceof Error ? error.message : "RFQ action failed",
      });
    },
    onSettled: () => {
      setMutatingId(null);
    },
  });

  const rfqs = rfqsQuery.data?.rfqs ?? [];
  const loadError = rfqsQuery.error ?? allRfqsQuery.error;

  const counts = useMemo(
    () => {
      const allRfqs = allRfqsQuery.data?.rfqs ?? [];

      return {
        pending: allRfqs.filter((rfq) => rfq.status === "PENDING_APPROVAL").length,
        approved: allRfqs.filter((rfq) => rfq.status === "APPROVED").length,
        compliance: allRfqs.filter((rfq) =>
          ["COMPLIANCE_REVIEW", "REVIEW_REQUESTED"].includes(rfq.status ?? "")
        ).length,
        total: allRfqsQuery.data?.total ?? allRfqs.length,
      };
    },
    [allRfqsQuery.data]
  );

  function runAction(rfq: RFQ, action: RFQAction) {
    const rfqId = rfq.rfq_id ?? rfq.id;

    if (!rfqId) return;

    setFeedback(null);
    actionMutation.mutate({ rfqId, action });
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-950">
            RFQ Decision Center
          </h1>
          <p className="mt-2 max-w-3xl text-slate-600">
            Compare alternate suppliers, review approval blockers, and persist
            sourcing decisions to the backend audit trail.
          </p>
        </div>

        <Button
          variant="outline"
          onClick={() => {
            allRfqsQuery.refetch();
            rfqsQuery.refetch();
          }}
          disabled={allRfqsQuery.isFetching || rfqsQuery.isFetching}
        >
          {allRfqsQuery.isFetching || rfqsQuery.isFetching ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <RefreshCcw className="mr-2 h-4 w-4" />
          )}
          Refresh
        </Button>
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
          detail="Persisted approval decisions"
          icon={CheckCircle2}
        />
        <OverviewCard
          title="Compliance Review"
          value={counts.compliance}
          detail="Review or compliance queue"
          icon={ShieldCheck}
        />
        <OverviewCard
          title="Total RFQs"
          value={counts.total}
          detail="Backend RFQ records"
          icon={RadioTower}
        />
      </div>

      {feedback ? (
        <div
          className={`rounded-lg border px-4 py-3 text-sm ${
            feedback.tone === "success"
              ? "border-emerald-200 bg-emerald-50 text-emerald-900"
              : "border-red-200 bg-red-50 text-red-900"
          }`}
        >
          {feedback.message}
        </div>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Find RFQs</CardTitle>
          <CardDescription>
            Search by supplier name, supplier code, RFQ ID, or workflow context.
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
              onChange={(event) => setStatusFilter(event.target.value as RFQReviewStatus)}
              className="h-11 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-4 text-sm outline-none transition focus:border-slate-400"
            >
              {statusOptions.map((status) => (
                <option key={status.value} value={status.value}>
                  {status.label}
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
            Compare price, lead time, risk, and review status before acting.
          </CardDescription>
        </CardHeader>

        <CardContent>
          {rfqsQuery.isLoading || allRfqsQuery.isLoading ? (
            <div className="flex items-center gap-2 py-8 text-sm text-slate-600">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading RFQ recommendations
            </div>
          ) : rfqsQuery.isError || allRfqsQuery.isError ? (
            <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-700" />
              <div>
                <div className="font-semibold text-red-950">
                  Failed to load RFQs
                </div>
                <p className="mt-1 text-sm text-red-800">
                  {loadError instanceof Error
                    ? loadError.message
                    : "Unknown backend error"}
                </p>
              </div>
            </div>
          ) : rfqs.length ? (
            <div className="space-y-4">
              {rfqs.map((rfq) => {
                const rfqId = rfq.rfq_id ?? rfq.id ?? "unknown-rfq";
                const supplierCode = rfq.supplier_code ?? rfq.supplier_id ?? "Unknown code";
                const isMutating = mutatingId === rfqId && actionMutation.isPending;

                return (
                  <div key={rfqId} className="rounded-lg border bg-white p-5">
                    <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <div className="min-w-0 font-semibold text-slate-950">
                            <div className="truncate">{rfq.supplier_name ?? "Unknown supplier"}</div>
                            <div className="font-mono text-xs font-normal text-slate-500">
                              {supplierCode}
                            </div>
                          </div>
                          <span
                            className={`rounded-full px-2 py-0.5 text-xs font-semibold ${getStatusClass(
                              rfq.status
                            )}`}
                          >
                            {statusLabel(rfq.status)}
                          </span>
                        </div>

                        <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-xs text-slate-400">
                          <span className="break-all font-mono">RFQ {rfqId}</span>
                          {rfq.workflow_id ? (
                            <span className="break-all font-mono">Workflow {rfq.workflow_id}</span>
                          ) : null}
                        </div>

                        <div className="mt-3 grid gap-3 md:grid-cols-3">
                          <DataTile label="Price" value={formatRFQPrice(rfq)} />
                          <DataTile label="Lead Time" value={formatLeadTime(rfq)} />
                          <DataTile label="Risk" value={rfq.risk_summary ?? "See workflow risk"} />
                        </div>

                        <div className="mt-4 rounded-lg bg-slate-50 p-3">
                          <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
                            Review Notes
                          </div>
                          <div className="mt-1 text-sm text-slate-700">
                            {rfq.notes ??
                              "Backend-persisted RFQ awaiting procurement review."}
                          </div>
                        </div>
                      </div>

                      <div className="flex w-full flex-col gap-2 xl:w-44">
                        <Button
                          onClick={() => runAction(rfq, "approve")}
                          disabled={isMutating || rfq.status === "APPROVED"}
                        >
                          {isMutating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                          Approve RFQ
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => runAction(rfq, "request-review")}
                          disabled={
                            isMutating ||
                            rfq.status === "REVIEW_REQUESTED" ||
                            rfq.status === "COMPLIANCE_REVIEW"
                          }
                        >
                          Request Review
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => runAction(rfq, "reject")}
                          disabled={isMutating || rfq.status === "REJECTED"}
                        >
                          Reject
                        </Button>
                        <div className="text-xs leading-5 text-slate-500">
                          Actions are persisted with audit history.
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="rounded-lg border border-dashed p-8 text-center">
              <div className="font-semibold text-slate-950">No RFQs found</div>
              <p className="mt-1 text-sm text-slate-600">
                Clear filters or seed RFQ records to see procurement decisions.
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

function statusLabel(status?: string | null) {
  return normalizeStatus(status).replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatRFQPrice(rfq: RFQ) {
  const price = rfq.price ?? getRfqTargetPrice(rfq);

  if (rfq.currency && rfq.currency !== "USD" && price !== null && price !== undefined) {
    return `${new Intl.NumberFormat("en-US").format(price)} ${rfq.currency}`;
  }

  return formatCurrency(price);
}

function formatLeadTime(rfq: RFQ) {
  if (rfq.lead_time_days !== null && rfq.lead_time_days !== undefined) {
    return `${rfq.lead_time_days} days`;
  }

  return formatDate(rfq.response_deadline);
}
