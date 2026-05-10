"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquareText, Shield } from "lucide-react";

const labels: Record<string, string> = {
  "/": "Operations Center",
  "/demo/run": "AI Investigation",
  "/workflows": "Incident Management",
  "/analytics": "Risk Intelligence",
  "/rfqs": "RFQ Command Center",
  "/settings": "Platform Settings",
};

const descriptions: Record<string, string> = {
  "/": "Monitor supplier risk, pending decisions, and operational exposure.",
  "/demo/run": "Ask questions, investigate suppliers, and trigger agent workflows.",
  "/workflows": "Review AI investigations, workflow status, and incident history.",
  "/analytics": "Track risk trends, supplier performance, and exposure patterns.",
  "/rfqs": "Review generated RFQs, approvals, and supplier quote actions.",
  "/settings": "Manage integrations, automation rules, and AI behavior.",
};

function getLabel(pathname: string) {
  if (pathname.startsWith("/workflows/")) {
    return "Incident Detail";
  }

  return labels[pathname] ?? "SupplyChain Guardian";
}

function getDescription(pathname: string) {
  if (pathname.startsWith("/workflows/")) {
    return "Review the full agent timeline, risk reasoning, RFQs, and compliance audit.";
  }

  return descriptions[pathname] ?? "AI-powered supply chain risk operations.";
}

export function Topbar() {
  const pathname = usePathname();
  const label = getLabel(pathname);
  const description = getDescription(pathname);

  return (
    <header className="sticky top-0 z-10 border-b bg-white/95 backdrop-blur">
      <div className="flex min-h-16 items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-950 text-white lg:hidden">
            <Shield className="h-4 w-4" />
          </div>

          <div className="min-w-0">
            <div className="text-sm text-muted-foreground">
              SupplyChain Guardian
            </div>
            <div className="truncate font-semibold text-slate-950">{label}</div>
            <div className="hidden truncate text-xs text-slate-500 sm:block">
              {description}
            </div>
          </div>
        </div>

        <Link
          href="/demo/run"
          className="inline-flex h-10 shrink-0 items-center justify-center rounded-md bg-slate-950 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
        >
          <MessageSquareText className="mr-2 h-4 w-4" />
          Investigate
        </Link>
      </div>
    </header>
  );
}