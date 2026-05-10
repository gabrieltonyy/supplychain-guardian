import {
  Bell,
  Bot,
  Database,
  Mail,
  Shield,
  SlidersHorizontal,
  Workflow,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const integrations = [
  {
    title: "ERP procurement data",
    detail: "SAP / Oracle integration for orders, suppliers, and spend data.",
    icon: Database,
    status: "Future",
  },
  {
    title: "Email notifications",
    detail: "RFQ approval requests and operational escalation messages.",
    icon: Mail,
    status: "Future",
  },
  {
    title: "Compliance screening",
    detail: "Sanctions and trade-control checks through workflow audit data.",
    icon: Shield,
    status: "Workflow data",
  },
];

const automationRules = [
  {
    title: "Risk threshold",
    value: "70+",
    detail: "Generate mitigation workflow above this risk score.",
    status: "Planned setting",
  },
  {
    title: "RFQ approval threshold",
    value: "$100K",
    detail: "Require human approval above this estimated sourcing value.",
    status: "Planned setting",
  },
  {
    title: "Compliance hold",
    value: "Always review",
    detail: "Restricted-market or sanctions signals must block execution.",
    status: "Workflow data",
  },
  {
    title: "Executive escalation",
    value: "Critical",
    detail: "Critical supplier risk should appear in the operations overview.",
    status: "Dashboard rule",
  },
];

const aiBehavior = [
  {
    title: "Risk explanation",
    detail: "AI can summarize supplier risk and operational impact.",
    status: "Active workflow",
  },
  {
    title: "Mitigation recommendations",
    detail: "AI can compare supplier alternatives and explain trade-offs.",
    status: "Active workflow",
  },
  {
    title: "RFQ preparation",
    detail: "AI can prepare RFQ data for human review.",
    status: "Review required",
  },
  {
    title: "Autonomous dispatch",
    detail: "Supplier dispatch without human approval is not enabled.",
    status: "Future",
  },
];

const notifications = [
  "Critical risk alerts",
  "RFQ approval requests",
  "Compliance escalation warnings",
  "Workflow failure notifications",
];

const futureCapabilities = [
  "Conversational operations assistant",
  "Human approval routing and escalation workflows",
  "Autonomous supplier negotiation with policy controls",
  "Long-running workflow memory and self-replanning",
];

function statusClass(status: string) {
  if (status.includes("Active") || status.includes("Workflow") || status.includes("Dashboard")) {
    return "border-emerald-200 bg-emerald-50 text-emerald-700";
  }

  if (status.includes("Review")) {
    return "border-orange-200 bg-orange-50 text-orange-700";
  }

  return "border-slate-200 bg-slate-50 text-slate-700";
}

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-950">
          Platform Settings
        </h1>
        <p className="mt-2 max-w-3xl text-slate-600">
          Review operational controls, approval thresholds, AI behavior, and
          platform capabilities. Unavailable settings are clearly marked.
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        {integrations.map((item) => {
          const Icon = item.icon;

          return (
            <Card key={item.title}>
              <CardHeader>
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-700">
                  <Icon className="h-5 w-5" />
                </div>
                <div className="flex items-start justify-between gap-3">
                  <CardTitle className="text-lg">{item.title}</CardTitle>
                  <Badge className={`${statusClass(item.status)} border`}>
                    {item.status}
                  </Badge>
                </div>
                <CardDescription>{item.detail}</CardDescription>
              </CardHeader>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-700">
              <Workflow className="h-5 w-5" />
            </div>
            <CardTitle>Automation Rules</CardTitle>
            <CardDescription>
              Thresholds and controls that should govern workflow execution.
            </CardDescription>
          </CardHeader>

          <CardContent className="grid gap-3 sm:grid-cols-2">
            {automationRules.map((rule) => (
              <div key={rule.title} className="rounded-lg border bg-white p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-semibold text-slate-950">
                      {rule.title}
                    </div>
                    <div className="mt-1 text-2xl font-bold text-slate-950">
                      {rule.value}
                    </div>
                  </div>
                  <Badge className={`${statusClass(rule.status)} border`}>
                    {rule.status}
                  </Badge>
                </div>
                <p className="mt-2 text-sm text-slate-500">{rule.detail}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50 text-violet-700">
              <Bot className="h-5 w-5" />
            </div>
            <CardTitle>AI Agent Behavior</CardTitle>
            <CardDescription>
              What AI agents can do today and what still requires humans.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-3">
            {aiBehavior.map((rule) => (
              <div key={rule.title} className="rounded-lg border bg-white p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="font-semibold text-slate-950">
                    {rule.title}
                  </div>
                  <Badge className={`${statusClass(rule.status)} border`}>
                    {rule.status}
                  </Badge>
                </div>
                <p className="mt-1 text-sm text-slate-500">{rule.detail}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-orange-50 text-orange-700">
              <Bell className="h-5 w-5" />
            </div>
            <CardTitle>Notification Preferences</CardTitle>
            <CardDescription>
              Planned alert categories for operational users.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-3">
            {notifications.map((notification) => (
              <div
                key={notification}
                className="flex items-center justify-between gap-3 rounded-lg border bg-white p-3 text-sm text-slate-700"
              >
                <span>{notification}</span>
                <Badge className="border-slate-200 bg-slate-50 text-slate-700">
                  Future
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
              <SlidersHorizontal className="h-5 w-5" />
            </div>
            <CardTitle>Future Platform Capabilities</CardTitle>
            <CardDescription>
              Not available yet. Included to show intended platform direction.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-3">
            {futureCapabilities.map((capability) => (
              <div key={capability} className="rounded-lg border bg-white p-3">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <span className="text-sm text-slate-700">{capability}</span>
                  <Badge className="border-slate-200 bg-slate-50 text-slate-700">
                    Future
                  </Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
