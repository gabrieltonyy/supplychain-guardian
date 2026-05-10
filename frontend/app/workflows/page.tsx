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
  formatDate,
  getStatusBadgeColor,
  getWorkflowStatus,
  normalizeStatus,
} from "@/lib/utils";

const supplierProfiles: Record<
  string,
  {
    incident: string;
    severity: "Critical" | "High" | "Medium" | "Low";
    impact: string;
    exposure: string;
    action: string;
  }
> = {
  "SUP-CN-001": {
    incident: "China semiconductor supply disruption",
    severity: "Critical",
    impact: "Projected 12-day delivery delay",
    exposure: "$1.4M",
    action: "Approve alternate sourcing RFQ",
  },
  "SUP-DE-001": {
    incident: "Backup supplier continuity review",
    severity: "Low",
    impact: "Stable supplier with backup capacity",
    exposure: "$620K",
    action: "Keep as preferred mitigation option",
  },
  "SUP-US-001": {
    incident: "High-cost alternate supplier review",
    severity: "Medium",
    impact: "Short lead time but higher unit cost",
    exposure: "$780K",
    action: "Compare against EU backup options",
  },
  "SUP-IN-001": {
    incident: "Lead-time anomaly investigation",
    severity: "Medium",
    impact: "Lead time increased by 6 days",
    exposure: "$510K",
    action: "Request updated delivery commitment",
  },
  "SUP-IR-001": {
    incident: "Trade compliance hold",
    severity: "High",
    impact: "Compliance review required before execution",
    exposure: "$420K",
    action: "Escalate to compliance officer",
  },
};

function getIncidentProfile(supplierId?: string | null) {
  if (!supplierId) {
    return {
      incident: "Supplier investigation",
      severity: "Medium" as const,
      impact: "Operational impact pending review",
      exposure: "TBD",
      action: "Open investigation detail",
    };
  }

  return (
    supplierProfiles[supplierId] ?? {
      incident: "Supplier risk investigation",
      severity: "Medium" as const,
      impact: "Risk assessment available in workflow detail",
      exposure: "TBD",
      action: "Review agent recommendation",
    }
  );
}

function getSeverityClass(severity: string) {
  switch (severity) {
    case "Critical":
      return "bg-red-50 text-red-700 border-red-200";
    case "High":
      return "bg-orange-50 text-orange-700 border-orange-200";
    case "Medium":
      return "bg-amber-50 text-amber-700 border-amber-200";
    default:
      return "bg-emerald-50 text-emerald-700 border-emerald-200";
  }
}

export default function WorkflowsPage() {
  const runsQuery = useQuery({
    queryKey: ["workflow-runs"],
    queryFn: () => apiClient.listWorkflowRuns(25),
  });

  const runs = runsQuery.data?.runs ?? [];
  const openInvestigations = runs.length;
  const failedRuns = runs.filter((run) =>
    normalizeStatus(getWorkflowStatus(run)).toLowerCase().includes("failed")
  ).length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-950">
            Incident Management
          </h1>
          <p className="mt-2 max-w-3xl text-slate-600">
            Review AI investigations as operational incidents: supplier,
            severity, impact, recommended action, and workflow trace.
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

      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard
          icon={FileWarning}
          label="Recent investigations"
          value={openInvestigations}
          detail="Latest 25 workflow-backed incidents"
        />
        <MetricCard
          icon={ShieldAlert}
          label="Failed or blocked"
          value={failedRuns}
          detail="Need technical or operations review"
        />
        <MetricCard
          icon={DollarSign}
          label="Tracked exposure"
          value="$2.3M"
          detail="Demo exposure represented by active suppliers"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Incidents</CardTitle>
          <CardDescription>
            Click an incident to inspect the full agent timeline and replay data.
          </CardDescription>
        </CardHeader>

        <CardContent>
          {runsQuery.isLoading ? (
            <div className="flex items-center gap-2 py-8 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading incident history
            </div>
          ) : runsQuery.isError ? (
            <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4">
              <AlertCircle className="mt-0.5 h-5 w-5 text-red-700" />
              <div>
                <div className="font-semibold text-red-950">
                  Unable to load incidents
                </div>
                <p className="mt-1 text-sm text-red-800">
                  {runsQuery.error instanceof Error
                    ? runsQuery.error.message
                    : "Unknown backend error"}
                </p>
              </div>
            </div>
          ) : runs.length ? (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1050px] text-left text-sm">
                <thead>
                  <tr className="border-b text-xs uppercase tracking-wide text-slate-500">
                    <th className="px-3 py-3 font-semibold">Incident</th>
                    <th className="px-3 py-3 font-semibold">Supplier</th>
                    <th className="px-3 py-3 font-semibold">Severity</th>
                    <th className="px-3 py-3 font-semibold">Status</th>
                    <th className="px-3 py-3 font-semibold">Impact</th>
                    <th className="px-3 py-3 font-semibold">Action</th>
                    <th className="px-3 py-3 font-semibold">Started</th>
                    <th className="px-3 py-3 font-semibold">Open</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map((run) => {
                    const status = getWorkflowStatus(run);
                    const profile = getIncidentProfile(run.supplier_id);

                    return (
                      <tr
                        key={run.workflow_id}
                        className="border-b last:border-0 hover:bg-slate-50"
                      >
                        <td className="px-3 py-4">
                          <Link
                            href={`/workflows/${run.workflow_id}`}
                            className="font-semibold text-slate-950 hover:underline"
                          >
                            {profile.incident}
                          </Link>
                          <div className="mt-1 max-w-[220px] truncate font-mono text-xs text-slate-400">
                            {run.workflow_id}
                          </div>
                        </td>

                        <td className="px-3 py-4 font-medium">
                          {run.supplier_id}
                        </td>

                        <td className="px-3 py-4">
                          <span
                            className={`inline-flex rounded-full border px-2 py-0.5 text-xs font-semibold ${getSeverityClass(
                              profile.severity
                            )}`}
                          >
                            {profile.severity}
                          </span>
                        </td>

                        <td className="px-3 py-4">
                          <Badge
                            className={`${getStatusBadgeColor(
                              status
                            )} capitalize`}
                          >
                            {normalizeStatus(status)}
                          </Badge>
                        </td>

                        <td className="px-3 py-4 text-slate-600">
                          <div>{profile.impact}</div>
                          <div className="mt-1 text-xs text-slate-400">
                            Exposure: {profile.exposure}
                          </div>
                        </td>

                        <td className="px-3 py-4 text-slate-600">
                          {profile.action}
                        </td>

                        <td className="px-3 py-4 text-slate-600">
                          {formatDate(run.started_at)}
                        </td>

                        <td className="px-3 py-4">
                          <Link
                            href={`/workflows/${run.workflow_id}`}
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
              <p className="mt-1 text-sm text-muted-foreground">
                Run an AI investigation to create persistent incident history.
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