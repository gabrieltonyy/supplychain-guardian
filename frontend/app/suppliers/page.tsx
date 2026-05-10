import Link from "next/link";
import { ArrowRight, FileWarning } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  getSeverityClass,
  supplierProfiles,
} from "@/lib/operational-data";

export default function SuppliersPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-950">
          Suppliers
        </h1>
        <p className="mt-2 max-w-3xl text-slate-600">
          Demo supplier context used by investigations, incidents, RFQs, and
          compliance review.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {supplierProfiles.map((supplier) => (
          <Card key={supplier.id}>
            <CardHeader>
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <CardTitle className="break-words text-lg">
                    {supplier.name}
                  </CardTitle>
                  <CardDescription className="break-all">
                    {supplier.id} · {supplier.region} · {supplier.category}
                  </CardDescription>
                </div>
                <Badge className={`${getSeverityClass(supplier.severity)} border`}>
                  {supplier.severity}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-2">
                <DataPoint label="Exposure" value={supplier.exposure} />
                <DataPoint label="Impact" value={supplier.impact} />
              </div>

              <div className="rounded-lg bg-slate-50 p-3 text-sm text-slate-700">
                <div className="mb-1 font-medium text-slate-950">
                  Recommended action
                </div>
                {supplier.recommendedAction}
              </div>

              <Link
                href="/demo/run"
                className="inline-flex h-10 w-full items-center justify-center rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-slate-50"
              >
                <FileWarning className="mr-2 h-4 w-4" />
                Investigate Supplier
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

function DataPoint({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-white p-3">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </div>
      <div className="mt-1 text-sm font-semibold text-slate-950">{value}</div>
    </div>
  );
}
