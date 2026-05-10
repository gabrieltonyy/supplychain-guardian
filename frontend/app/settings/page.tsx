import {
  Bell,
  Bot,
  Database,
  Mail,
  Shield,
  SlidersHorizontal,
  Workflow,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const integrationItems = [
  {
    title: "ERP Integration",
    detail: "SAP / Oracle ERP connectivity for procurement and sourcing data.",
    icon: Database,
  },
  {
    title: "Email Notifications",
    detail: "RFQ approvals, escalation alerts, and workflow notifications.",
    icon: Mail,
  },
  {
    title: "Compliance Monitoring",
    detail: "Trade restriction and regulatory screening integrations.",
    icon: Shield,
  },
];

const automationRules = [
  "Auto-generate mitigation workflows above risk score 70",
  "Require approval for RFQs above $100K",
  "Escalate compliance workflows automatically",
  "Flag high-risk suppliers for executive review",
];

const aiBehavior = [
  "Enable autonomous supplier ranking",
  "Allow AI-generated mitigation recommendations",
  "Use workflow replay for operational intelligence",
  "Enable future conversational investigation assistant",
];

const notifications = [
  "Critical risk alerts",
  "RFQ approval requests",
  "Compliance escalation warnings",
  "Workflow failure notifications",
];

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-950">
          Platform Settings
        </h1>

        <p className="mt-2 max-w-3xl text-slate-600">
          Configure operational integrations, automation rules, AI behavior,
          approval requirements, and notification preferences for the Supply
          Chain Operations Center.
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        {integrationItems.map((item) => {
          const Icon = item.icon;

          return (
            <Card key={item.title}>
              <CardHeader>
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-700">
                  <Icon className="h-5 w-5" />
                </div>

                <CardTitle>{item.title}</CardTitle>

                <CardDescription>
                  {item.detail}
                </CardDescription>
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
              Operational logic and approval thresholds that influence workflow
              execution.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-3">
            {automationRules.map((rule) => (
              <div
                key={rule}
                className="rounded-lg border bg-white p-3 text-sm text-slate-700"
              >
                {rule}
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
              Configure how AI agents participate in operational workflows.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-3">
            {aiBehavior.map((rule) => (
              <div
                key={rule}
                className="rounded-lg border bg-white p-3 text-sm text-slate-700"
              >
                {rule}
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
              Configure which operational alerts should notify users.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-3">
            {notifications.map((notification) => (
              <div
                key={notification}
                className="rounded-lg border bg-white p-3 text-sm text-slate-700"
              >
                {notification}
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
              <SlidersHorizontal className="h-5 w-5" />
            </div>

            <CardTitle>Future Platform Direction</CardTitle>

            <CardDescription>
              Features planned for autonomous supply chain orchestration.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-3 text-sm text-slate-700">
            <div className="rounded-lg border bg-white p-3">
              Agent-to-agent reflection and debate loops
            </div>

            <div className="rounded-lg border bg-white p-3">
              Conversational operations assistant
            </div>

            <div className="rounded-lg border bg-white p-3">
              Autonomous RFQ dispatch and supplier negotiation
            </div>

            <div className="rounded-lg border bg-white p-3">
              Human approval routing and escalation workflows
            </div>

            <div className="rounded-lg border bg-white p-3">
              Long-running workflow memory and self-replanning
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}