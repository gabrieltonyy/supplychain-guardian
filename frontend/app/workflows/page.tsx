"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  AlertCircle,
  ArrowRight,
  DollarSign,
  FileWarning,
  Loader2,
  RefreshCcw,
  ShieldAlert,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
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
  getStatusBadgeColor,
  getWorkflowStatus,
  normalizeStatus,
} from "@/lib/utils";
import { getSeverityClass } from "@/lib/operational-data";
import { normalizeWorkflowRun } from "@/lib/workflow-normalizers";

export default function WorkflowsPage() {
  const runsQuery = useQuery({
    queryKey: ["workflow-runs"],
    queryFn: () => apiClient.listWorkflowRuns(25),
  });

  const runs = runsQuery.data?.runs ?? [];
  const incidents = runs.map(normalizeWorkflowRun);
  const totalIncidents = runs.length;
  const failedRuns = runs.filter((run) =>
    normalizeStatus(getWorkflowStatus(run)).toLowerCase().includes("failed")
  ).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-950">
            Incident Management
          </h1>
          <p className="mt-2 max-w-3xl text-slate-600">
            Review supplier risks as incidents: severity, impact, recommended
            action, and workflow status
          </p>
        </div>

        <Button
          variant="outline"
          onClick={() => runsQuery.refetch()}
          disabled={runsQuery.isFetching}
        >
          {runsQuery.isFetching ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <RefreshCcw className="mr-2 h-4 w-4" />
          )}
          Refresh
        </Button>
      </div>

      {/* Summary Metrics */}
      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard
          icon={FileWarning}
          label="Recent Incidents"
          value={totalIncidents}
          detail="Latest 25 investigations"
        />
        <MetricCard
          icon={ShieldAlert}
          label="Failed/Blocked"
          value={failedRuns}
          detail="Need technical review"
        />
        <MetricCard
          icon={DollarSign}
          label="Tracked Exposure"
          value="$2.3M"
          detail="Active supplier exposure"
        />
      </div>

      {/* Incidents Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Incidents</CardTitle>
          <CardDescription>
            Click an incident to see full agent timeline and details
          </CardDescription>
        </CardHeader>

        <CardContent>
          {runsQuery.isLoading ? (
            <div className="flex items-center gap-2 py-8 text-sm text-slate-600">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading incident history...
            </div>
          ) : runsQuery.isError ? (
            <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-700" />
              <div>
                <div className="font-semibold text-red-950">
                  Unable to load incidents
                </div>
                <p className="mt-1 text-sm text-red-800">
                  {runsQuery.error instanceof Error
                    ? runsQuery.error.message
                    : "Unknown error"}
                </p>
              </div>
            </div>
          ) : runs.length ? (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1000px] text-left text-sm">
                <thead>
                  <tr className="border-b text-xs font-semibold uppercase tracking-wide text-slate-500">
                    <th className="px-3 py-3">Incident</th>
                    <th className="px-3 py-3">Supplier</th>
                    <th className="px-3 py-3">Severity</th>
                    <th className="px-3 py-3">Status</th>
                    <th className="px-3 py-3">Impact</th>
                    <th className="px-3 py-3">Action</th>
                    <th className="px-3 py-3">Started</th>
                    <th className="px-3 py-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.map((incident) => {
                    return (
                      <tr
                        key={incident.workflowId}
                        className="border-b last:border-0 hover:bg-slate-50"
                      >
                        {/* Incident Name */}
                        <td className="px-3 py-4">
                          <Link
                            href={`/workflows/${incident.workflowId}`}
                            className="font-semibold text-slate-950 hover:underline"
                          >
                            {incident.incident}
                          </Link>
                          <div className="mt-1 max-w-[200px] truncate font-mono text-xs text-slate-400">
                            {incident.workflowId}
                          </div>
                        </td>

                        {/* Supplier */}
                        <td className="px-3 py-4 font-medium text-slate-950">
                          {incident.supplierId}
                        </td>

                        {/* Severity */}
                        <td className="px-3 py-4">
                          <span
                            className={`inline-flex rounded-full border px-2 py-0.5 text-xs font-semibold ${getSeverityClass(
                              incident.severity
                            )}`}
                          >
                            {incident.severity}
                          </span>
                        </td>

                        {/* Workflow Status */}
                        <td className="px-3 py-4">
                          <Badge
                            className={`${getStatusBadgeColor(
                              incident.status
                            )} capitalize`}
                          >
                            {incident.statusLabel}
                          </Badge>
                        </td>

                        {/* Impact */}
                        <td className="px-3 py-4">
                          <div className="text-slate-700">{incident.impact}</div>
                          <div className="mt-1 text-xs text-slate-500">
                            Exposure: {incident.exposure}
                          </div>
                        </td>

                        {/* Recommended Action */}
                        <td className="px-3 py-4 text-slate-600">
                          {incident.recommendedAction}
                        </td>

                        {/* Started */}
                        <td className="px-3 py-4 text-slate-600">
                          {incident.startedAt}
                        </td>

                        {/* Open Link */}
                        <td className="px-3 py-4">
                          <Link
                            href={`/workflows/${incident.workflowId}`}
                            className="inline-flex items-center text-sm font-medium text-slate-950 hover:underline"
                          >
                            Detail
                            <ArrowRight className="ml-1 h-4 w-4" />
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="rounded-lg border border-dashed p-8 text-center">
              <div className="font-semibold text-slate-950">
                No incidents yet
              </div>
              <p className="mt-1 text-sm text-slate-600">
                Run an AI investigation to create incident history
              </p>
              <Link
                href="/demo/run"
                className="mt-4 inline-flex h-10 items-center justify-center rounded-md bg-slate-950 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
              >
                Start Investigation
              </Link>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  detail,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string | number;
  detail: string;
}) {
  return (
    <Card>
      <CardContent className="flex items-start justify-between gap-3 p-5">
        <div>
          <div className="text-sm font-medium text-slate-500">{label}</div>
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
