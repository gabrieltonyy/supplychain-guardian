import Link from "next/link";
import { AlertTriangle, BarChart3, FileWarning, MessageSquareText } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const riskViews = [
  {
    href: "/demo/run",
    icon: MessageSquareText,
    title: "Investigate a supplier",
    detail: "Ask why a supplier is risky and generate mitigation options.",
  },
  {
    href: "/workflows",
    icon: FileWarning,
    title: "Review incidents",
    detail: "Open workflow-backed incidents and inspect recommended actions.",
  },
  {
    href: "/analytics",
    icon: BarChart3,
    title: "View risk intelligence",
    detail: "See risk distribution, supplier ranking, and exposure patterns.",
  },
];

export default function RisksPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-950">
          Risk Workbench
        </h1>
        <p className="mt-2 max-w-3xl text-slate-600">
          Risk outputs are handled through investigations, incident detail, and
          management analytics.
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-orange-50 text-orange-700">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <CardTitle>Where to Review Risk</CardTitle>
          <CardDescription>
            Choose the workflow based on the decision you need to make.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          {riskViews.map((view) => {
            const Icon = view.icon;

            return (
              <Link
                key={view.title}
                href={view.href}
                className="rounded-lg border bg-white p-4 transition hover:border-slate-300 hover:shadow-sm"
              >
                <Icon className="mb-2 h-5 w-5 text-slate-600" />
                <div className="font-semibold text-slate-950">{view.title}</div>
                <p className="mt-1 text-sm text-slate-500">{view.detail}</p>
              </Link>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}
