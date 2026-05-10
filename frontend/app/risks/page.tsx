import Link from "next/link";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function RisksPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-950">Risk Workbench</h1>
        <p className="mt-2 text-slate-600">
          Risk outputs are available in workflow detail and demo run views.
        </p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Primary Risk Views</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Link className="font-medium text-slate-950 underline" href="/demo/run">
            Run demo workflow
          </Link>
          <Link className="font-medium text-slate-950 underline" href="/workflows">
            Browse workflow runs
          </Link>
          <Link className="font-medium text-slate-950 underline" href="/analytics">
            View analytics
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
