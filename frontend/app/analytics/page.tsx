"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  AlertCircle,
  ArrowUpRight,
  DollarSign,
  Loader2,
  RefreshCcw,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { apiClient } from "@/lib/api-client";

const riskColors: Record<string, string> = {
  LOW: "#10b981",
  MEDIUM: "#f59e0b",
  HIGH: "#f97316",
  CRITICAL: "#ef4444",
};

const riskInsights = [
  {
    label: "Semiconductor sourcing",
    trend: "Risk up",
    detail: "China supplier disruption is the highest exposure item.",
  },
  {
    label: "Compliance exposure",
    trend: "Needs review",
    detail: "Trade-control review required for restricted supplier workflows.",
  },
  {
    label: "Mitigation readiness",
    trend: "Stable",
    detail: "Backup suppliers are available for semiconductor sourcing.",
  },
];

export default function AnalyticsPage() {
  const summaryQuery = useQuery({
    queryKey: ["analytics-summary"],
    queryFn: () => apiClient.getAnalyticsSummary(),
  });

  const distributionQuery = useQuery({
    queryKey: ["risk-distribution"],
    queryFn: () => apiClient.getRiskDistribution(),
  });

  const rankingsQuery = useQuery({
    queryKey: ["supplier-rankings"],
    queryFn: () => apiClient.getSupplierRankings(10),
  });

  const isLoading =
    summaryQuery.isLoading ||
    distributionQuery.isLoading ||
    rankingsQuery.isLoading;
  const isFetching =
    summaryQuery.isFetching ||
    distributionQuery.isFetching ||
    rankingsQuery.isFetching;
  const error = summaryQuery.error ?? distributionQuery.error ?? rankingsQuery.error;
  const summary = summaryQuery.data?.summary;

  const rankings =
    rankingsQuery.data?.rankings.map((ranking) => ({
      supplier_id: ranking.supplier_id,
      score: ranking.average_risk_score ?? ranking.avg_risk_score ?? 0,
      count: ranking.assessment_count ?? ranking.total_runs ?? 0,
    })) ?? [];

  const distribution = distributionQuery.data?.distribution ?? [];
  const criticalOrHighCount = distribution
    .filter((entry) => ["CRITICAL", "HIGH"].includes(entry.risk_level))
    .reduce((total, entry) => total + entry.count, 0);

  function refreshAll() {
    summaryQuery.refetch();
    distributionQuery.refetch();
    rankingsQuery.refetch();
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-950">
            Risk Intelligence
          </h1>
          <p className="mt-2 max-w-3xl text-slate-600">
            Translate workflow data into business insight: risk concentration,
            supplier exposure, failure patterns, and mitigation readiness.
          </p>
        </div>

        <Button variant="outline" onClick={refreshAll} disabled={isFetching}>
          {isFetching ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <RefreshCcw className="mr-2 h-4 w-4" />
          )}
          Refresh
        </Button>
      </div>

      {isLoading ? (
        <Card>
          <CardContent className="flex items-center gap-2 py-8 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading risk intelligence
          </CardContent>
        </Card>
      ) : error ? (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="flex items-start gap-3 pt-6">
            <AlertCircle className="mt-0.5 h-5 w-5 text-red-700" />
            <div>
              <div className="font-semibold text-red-950">
                Unable to load intelligence data
              </div>
              <p className="mt-1 text-sm text-red-800">
                {error instanceof Error ? error.message : "Unknown backend error"}
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <SummaryCard
              icon={TrendingUp}
              label="Total investigations"
              value={summary?.total_runs ?? 0}
              detail="Workflow-backed risk checks"
            />
            <SummaryCard
              icon={ShieldAlert}
              label="High/Critical risks"
              value={criticalOrHighCount}
              detail="Require management attention"
            />
            <SummaryCard
              icon={ArrowUpRight}
              label="Success rate"
              value={`${summary?.success_rate ?? 0}%`}
              detail="Completed workflow rate"
            />
            <SummaryCard
              icon={AlertCircle}
              label="Failed workflows"
              value={summary?.failed_runs ?? 0}
              detail="Need technical review"
            />
            <SummaryCard
              icon={DollarSign}
              label="Estimated exposure"
              value="$2.3M"
              detail="Demo operational exposure"
            />
          </div>

          <div className="grid gap-6 xl:grid-cols-3">
            <Card className="xl:col-span-2">
              <CardHeader>
                <CardTitle>Risk Distribution</CardTitle>
                <CardDescription>
                  How many supplier assessments fall into each risk band.
                </CardDescription>
              </CardHeader>
              <CardContent className="h-80">
                {distribution.length ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={distribution}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="risk_level" />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                        {distribution.map((entry) => (
                          <Cell
                            key={entry.risk_level}
                            fill={riskColors[entry.risk_level] ?? "#334155"}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <EmptyChartState message="No risk distribution data available yet." />
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Executive Insights</CardTitle>
                <CardDescription>
                  Operational signals that should influence decisions.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {riskInsights.map((insight) => (
                  <div key={insight.label} className="rounded-lg border p-3">
                    <div className="flex items-center justify-between gap-3">
                      <div className="font-medium text-slate-950">
                        {insight.label}
                      </div>
                      <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-700">
                        {insight.trend}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-slate-500">
                      {insight.detail}
                    </p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 xl:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Supplier Risk Ranking</CardTitle>
                <CardDescription>
                  Highest average risk score by supplier.
                </CardDescription>
              </CardHeader>
              <CardContent className="h-80">
                {rankings.length ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={rankings}
                      layout="vertical"
                      margin={{ left: 24 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                      <XAxis type="number" domain={[0, 100]} />
                      <YAxis dataKey="supplier_id" type="category" width={110} />
                      <Tooltip />
                      <Bar dataKey="score" fill="#334155" radius={[0, 6, 6, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <EmptyChartState message="No supplier ranking data available yet." />
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Mitigation Effectiveness</CardTitle>
                <CardDescription>
                  Management view of whether mitigations are reducing exposure.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Recommendation
                  title="Current signal"
                  detail="Generated mitigation plans and RFQs are visible, but shipment outcomes are not connected yet."
                />
                <Recommendation
                  title="Business value"
                  detail="Once fulfillment outcomes are connected, this view will show avoided delays and exposure reduction."
                />
                <Recommendation
                  title="Next data need"
                  detail="Connect order, shipment, and supplier response outcomes to prove mitigation impact."
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Operational Recommendations</CardTitle>
                <CardDescription>
                  What a supply chain manager should do next.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Recommendation
                  title="Prioritize high-risk suppliers"
                  detail="Review suppliers appearing in the top ranking before approving new sourcing actions."
                />
                <Recommendation
                  title="Move RFQs out of pending state"
                  detail="Pending RFQs represent the biggest delay between AI recommendation and business action."
                />
                <Recommendation
                  title="Track mitigation effectiveness"
                  detail="Later, connect shipment outcomes so the platform can prove whether mitigations prevented disruption."
                />
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}

function SummaryCard({
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

function EmptyChartState({ message }: { message: string }) {
  return (
    <div className="flex h-full items-center justify-center rounded-lg border border-dashed text-center text-sm text-slate-500">
      {message}
    </div>
  );
}

function Recommendation({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="font-semibold text-slate-950">{title}</div>
      <p className="mt-1 text-sm text-slate-500">{detail}</p>
    </div>
  );
}
