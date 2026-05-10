import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Clock,
  DollarSign,
  FileWarning,
  MessageSquareText,
  RadioTower,
  Shield,
  Truck,
  Zap,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const overviewMetrics = [
  {
    label: "Critical Incidents",
    value: "3",
    detail: "Require attention today",
    icon: AlertTriangle,
    tone: "text-red-600 bg-red-50 border-red-200",
  },
  {
    label: "Suppliers at Risk",
    value: "7",
    detail: "Across active supplier base",
    icon: FileWarning,
    tone: "text-orange-600 bg-orange-50 border-orange-200",
  },
  {
    label: "Pending RFQs",
    value: "12",
    detail: "Awaiting review or approval",
    icon: RadioTower,
    tone: "text-blue-600 bg-blue-50 border-blue-200",
  },
  {
    label: "Compliance Flags",
    value: "2",
    detail: "Need policy validation",
    icon: Shield,
    tone: "text-purple-600 bg-purple-50 border-purple-200",
  },
  {
    label: "Estimated Exposure",
    value: "$2.3M",
    detail: "Potential operational impact",
    icon: DollarSign,
    tone: "text-emerald-600 bg-emerald-50 border-emerald-200",
  },
];

const priorityIncidents = [
  {
    title: "China semiconductor supply risk",
    supplier: "SUP-CN-001",
    severity: "Critical",
    impact: "Projected 12-day delivery delay",
    exposure: "$1.4M",
    action: "Switch 40% sourcing to SUP-DE-001 and approve emergency RFQ.",
  },
  {
    title: "Restricted-market compliance review",
    supplier: "SUP-IR-001",
    severity: "High",
    impact: "Trade restriction review required before dispatch",
    exposure: "$420K",
    action: "Hold execution until compliance officer approval is completed.",
  },
  {
    title: "Supplier lead-time anomaly",
    supplier: "SUP-IN-001",
    severity: "Medium",
    impact: "Lead time increased by 6 days against baseline",
    exposure: "$180K",
    action: "Request alternate quotes and monitor logistics feeds.",
  },
];

const pendingDecisions = [
  {
    title: "Approve emergency RFQ",
    detail: "3 supplier quotes generated for semiconductor sourcing.",
    owner: "Procurement",
  },
  {
    title: "Review compliance hold",
    detail: "1 workflow requires sanctions and trade-control review.",
    owner: "Compliance",
  },
  {
    title: "Confirm mitigation plan",
    detail: "Risk agent recommends supplier diversification.",
    owner: "Supply Chain Ops",
  },
];

const monitoringSignals = [
  "Supplier risk scoring",
  "Logistics delay signals",
  "Weather disruption feeds",
  "Compliance screening",
  "RFQ automation",
  "Workflow audit trail",
];

const quickPrompts = [
  "Why is SUP-CN-001 high risk?",
  "Find safer alternatives for semiconductor supply.",
  "Show RFQs waiting for approval.",
  "Summarize compliance issues this week.",
];

export default function HomePage() {
  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <div className="inline-flex items-center gap-2 rounded-full border border-violet-200 bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700">
          <Shield className="h-3.5 w-3.5" />
          Powered by AMD Cloud GPU + ROCm + vLLM
        </div>

        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              Supply Chain Operations Center
            </h1>
            <p className="mt-2 max-w-3xl text-base text-slate-600 sm:text-lg">
              Monitor supplier risk, investigate disruptions, approve RFQs, and
              keep mitigation actions moving across the supply chain.
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
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
        {overviewMetrics.map((metric) => {
          const Icon = metric.icon;

          return (
            <Card key={metric.label} className="overflow-hidden">
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
          );
        })}
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Priority Incidents</CardTitle>
            <CardDescription>
              The most important supply chain risks requiring review or action.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {priorityIncidents.map((incident) => (
              <div
                key={incident.title}
                className="rounded-lg border bg-white p-4 transition hover:border-slate-300 hover:shadow-sm"
              >
                <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="font-semibold text-slate-950">
                        {incident.title}
                      </h3>
                      <span className="rounded-full bg-red-50 px-2 py-0.5 text-xs font-medium text-red-700">
                        {incident.severity}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-slate-500">
                      Supplier:{" "}
                      <span className="font-medium text-slate-700">
                        {incident.supplier}
                      </span>
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
                  <div className="rounded-md bg-slate-50 p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                      Business impact
                    </p>
                    <p className="mt-1 text-sm text-slate-700">
                      {incident.impact}
                    </p>
                  </div>
                  <div className="rounded-md bg-emerald-50 p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-emerald-700">
                      Recommended action
                    </p>
                    <p className="mt-1 text-sm text-emerald-800">
                      {incident.action}
                    </p>
                  </div>
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
              Human approvals and operational decisions blocking automation.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {pendingDecisions.map((decision) => (
              <div key={decision.title} className="rounded-lg border p-3">
                <div className="flex items-start gap-3">
                  <Clock className="mt-0.5 h-4 w-4 text-orange-500" />
                  <div>
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
            ))}

            <Link
              href="/rfqs"
              className="inline-flex h-10 w-full items-center justify-center rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-slate-50"
            >
              Review Approval Queue
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </CardContent>
        </Card>
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Ask SupplyChain Guardian</CardTitle>
            <CardDescription>
              A chat-first investigation experience for supply chain operators.
              The full backend chat orchestrator will be connected later.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-xl border bg-slate-50 p-4">
              <div className="flex items-start gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-950 text-white">
                  <MessageSquareText className="h-4 w-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-slate-950">
                    What would you like to investigate?
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    Ask about supplier risk, mitigation plans, RFQs, compliance
                    checks, or operational exposure.
                  </p>

                  <div className="mt-4 grid gap-2 sm:grid-cols-2">
                    {quickPrompts.map((prompt) => (
                      <Link
                        key={prompt}
                        href="/demo/run"
                        className="rounded-lg border bg-white px-3 py-2 text-sm text-slate-700 transition hover:border-slate-300 hover:bg-slate-100"
                      >
                        {prompt}
                      </Link>
                    ))}
                  </div>

                  <Link
                    href="/demo/run"
                    className="mt-4 inline-flex h-10 items-center justify-center rounded-md bg-slate-950 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
                  >
                    AI Investigation
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Monitoring Coverage</CardTitle>
            <CardDescription>
              Operational signals currently represented in the platform.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {monitoringSignals.map((signal) => (
              <div key={signal} className="flex items-center gap-3 text-sm">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                <span className="text-slate-700">{signal}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>

      <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
              <Truck className="h-5 w-5" />
            </div>
            <CardTitle className="text-lg">Operational Continuity</CardTitle>
            <CardDescription>
              Detect supplier, logistics, and regional disruptions before they
              affect fulfillment.
            </CardDescription>
          </CardHeader>
        </Card>

        <Card>
          <CardHeader>
            <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-purple-50 text-purple-600">
              <Zap className="h-5 w-5" />
            </div>
            <CardTitle className="text-lg">Agentic Mitigation</CardTitle>
            <CardDescription>
              Generate supplier alternatives, compare trade-offs, and prepare
              RFQs for human approval.
            </CardDescription>
          </CardHeader>
        </Card>

        <Card>
          <CardHeader>
            <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
              <BarChart3 className="h-5 w-5" />
            </div>
            <CardTitle className="text-lg">Risk Intelligence</CardTitle>
            <CardDescription>
              Track risk distribution, supplier rankings, compliance flags, and
              mitigation effectiveness.
            </CardDescription>
          </CardHeader>
        </Card>
      </section>
    </div>
  );
}