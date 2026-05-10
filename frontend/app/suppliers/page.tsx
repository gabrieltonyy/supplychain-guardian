import Link from "next/link";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const suppliers = ["SUP-CN-001", "SUP-DE-001", "SUP-US-001", "SUP-IN-001", "SUP-IR-001"];

export default function SuppliersPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-950">Suppliers</h1>
        <p className="mt-2 text-slate-600">Hackathon demo suppliers available for workflow runs.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {suppliers.map((supplierId) => (
          <Card key={supplierId}>
            <CardHeader>
              <CardTitle className="text-lg">{supplierId}</CardTitle>
              <CardDescription>Seed supplier profile</CardDescription>
            </CardHeader>
            <CardContent>
              <Link
                href={`/demo/run`}
                className="text-sm font-medium text-slate-950 underline"
              >
                Run workflow
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
