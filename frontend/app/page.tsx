import Link from "next/link";
import type { ComponentType } from "react";
import {
  AlertTriangle,
  ArrowRight,
  Clock,
  DollarSign,
  FileWarning,
  MessageSquareText,
  RadioTower,
  Shield,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  getSeverityClass,
  operationalMetrics,
  pendingDecisions,
  supplierProfiles,
} from "@/lib/operational-data";

const metricIcons: Record<string, ComponentType<{ className?: string }>> = {
  "Critical Incidents": AlertTriangle,
  "Pending RFQs": RadioTower,
  "Compliance Flags": Shield,
  "Estimated Exposure": DollarSign,
};

const priorityIncidents = supplierProfiles.filter((supplier) =>
  ["Critical", "High", "Medium"].includes(supplier.severity)
);

const quickActions = [
  {
    href: "/demo/run",
    icon: MessageSquareText,
    title: "Investigate Supplier Risk",
    detail: "Ask the AI agents what changed and what to do next.",
  },
  {
    href: "/rfqs",
    icon: RadioTower,
    title: "Review Pending RFQs",
    detail: "Approve, reject, or request review for sourcing options.",
  },
  {
    href: "/workflows",
    icon: FileWarning,
    title: "Open Incidents",
    detail: "Inspect supplier impact, workflow status, and audit trail.",
  },
  {
    href: "/analytics",
    icon: DollarSign,
    title: "Check Exposure",
    detail: "See risk concentration and management recommendations.",
  },
];

export default function HomePage() {
  return (
    <div className="space-y-6">
      <section className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
            Operations Center
          </h1>
          <p className="mt-2 max-w-3xl text-base text-slate-600">
            See what is risky, why it matters, and which supply chain decisions
            need approval today.
          </p>
        </div>

        <div className="flex flex-col gap-2 sm:flex-row">
          <Link
            href="/demo/run"
            className="inline-flex h-10 items-center justify-center rounded-md bg-slate-950 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
          >
            <MessageSquareText className="mr-2 h-4 w-4" />
            Start Investigation
          </Link>

          <Link
            href="/workflows"
            className="inline-flex h-10 items-center justify-center rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-slate-50"
          >
            View Incidents
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {operationalMetrics.map((metric) => {
          const Icon = metricIcons[metric.label] ?? Shield;

          return (
            <Link key={metric.label} href={metric.href} className="block">
              <Card className="h-full transition hover:border-slate-300 hover:shadow-md">
                <CardContent className="p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium text-slate-500">
                        {metric.label}
                      </p>
                      <p className="mt-2 text-3xl font-bold text-slate-950">
                        {metric.value}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        {metric.detail}
                      </p>
                    </div>
                    <div className={`rounded-lg border p-2 ${metric.tone}`}>
                      <Icon className="h-4 w-4" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Priority Incidents</CardTitle>
            <CardDescription>
              Supplier disruptions ordered by operational urgency.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {priorityIncidents.map((incident) => (
              <div key={incident.id} className="rounded-lg border bg-white p-4">
                <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="font-semibold text-slate-950">
                        {incident.incident}
                      </h3>
                      <span
                        className={`rounded-full border px-2 py-0.5 text-xs font-semibold ${getSeverityClass(
                          incident.severity
                        )}`}
                      >
                        {incident.severity}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-slate-500">
                      {incident.id} · {incident.name}
                    </p>
                  </div>

                  <div className="text-left sm:text-right">
                    <p className="text-xs text-slate-500">Exposure</p>
                    <p className="font-semibold text-slate-950">
                      {incident.exposure}
                    </p>
                  </div>
                </div>

                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  <DecisionTile
                    label="Why it matters"
                    value={incident.impact}
                    tone="bg-slate-50 text-slate-700"
                  />
                  <DecisionTile
                    label="Recommended action"
                    value={incident.recommendedAction}
                    tone="bg-emerald-50 text-emerald-800"
                  />
                </div>
              </div>
            ))}

            <Link
              href="/workflows"
              className="inline-flex h-10 w-full items-center justify-center rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-slate-50"
            >
              Open Incident Management
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pending Decisions</CardTitle>
            <CardDescription>
              Human approvals blocking the workflow.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {pendingDecisions.map((decision) => (
              <Link key={decision.title} href={decision.href} className="block">
                <div className="rounded-lg border p-3 transition hover:border-slate-300 hover:bg-slate-50">
                  <div className="flex items-start gap-3">
                    <Clock className="mt-0.5 h-4 w-4 shrink-0 text-orange-500" />
                    <div className="min-w-0">
                      <p className="font-medium text-slate-950">
                        {decision.title}
                      </p>
                      <p className="mt-1 text-sm text-slate-500">
                        {decision.detail}
                      </p>
                      <p className="mt-2 text-xs font-medium text-slate-500">
                        Owner: {decision.owner}
                      </p>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common operator tasks for investigation, approvals, and review.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {quickActions.map((action) => {
              const Icon = action.icon;

              return (
                <Link
                  key={action.title}
                  href={action.href}
                  className="rounded-lg border bg-white p-4 text-sm transition hover:border-slate-300 hover:shadow-sm"
                >
                  <Icon className="mb-2 h-5 w-5 text-slate-600" />
                  <div className="font-medium text-slate-950">
                    {action.title}
                  </div>
                  <div className="mt-1 text-xs leading-5 text-slate-500">
                    {action.detail}
                  </div>
                </Link>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <div className="rounded-lg border border-violet-200 bg-violet-50 p-4">
        <div className="flex items-start gap-3">
          <Shield className="mt-0.5 h-5 w-5 shrink-0 text-violet-700" />
          <div>
            <div className="font-semibold text-violet-900">
              AI-assisted, operator-approved workflow
            </div>
            <p className="mt-1 text-sm text-violet-700">
              Agent reasoning uses AMD ROCm + vLLM where available. Operators
              still review mitigation, RFQ, and compliance decisions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function DecisionTile({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: string;
}) {
  return (
    <div className={`rounded-md p-3 ${tone}`}>
      <p className="text-xs font-medium uppercase tracking-wide">{label}</p>
      <p className="mt-1 text-sm">{value}</p>
    </div>
  );
}
