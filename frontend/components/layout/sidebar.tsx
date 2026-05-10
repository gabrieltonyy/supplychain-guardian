"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  ClipboardCheck,
  FileWarning,
  MessageSquareText,
  RadioTower,
  Settings,
  Shield,
} from "lucide-react";

import { cn } from "@/lib/utils";

const navItems = [
  {
    href: "/",
    label: "Operations",
    description: "Live risk overview",
    icon: Shield,
  },
  {
    href: "/demo/run",
    label: "Investigate",
    description: "Ask AI or run analysis",
    icon: MessageSquareText,
  },
  {
    href: "/workflows",
    label: "Incidents",
    description: "Workflow investigations",
    icon: FileWarning,
  },
  {
    href: "/analytics",
    label: "Intelligence",
    description: "Risk trends and insights",
    icon: BarChart3,
  },
  {
    href: "/rfqs",
    label: "RFQs",
    description: "Quotes and approvals",
    icon: RadioTower,
  },
  {
    href: "/settings",
    label: "Settings",
    description: "Rules and integrations",
    icon: Settings,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-72 shrink-0 border-r bg-white lg:block">
      <div className="flex h-full flex-col">
        <div className="border-b px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-950 text-white">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <div className="font-semibold text-slate-950">
                SupplyChain Guardian
              </div>
              <div className="text-xs text-slate-500">
                AI Operations Center
              </div>
            </div>
          </div>
        </div>

        <nav className="space-y-1 px-3 py-4">
          {navItems.map((item) => {
            const isActive =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "group flex items-start gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition",
                  isActive
                    ? "bg-slate-950 text-white"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
                )}
              >
                <Icon className="mt-0.5 h-4 w-4 shrink-0" />
                <span className="min-w-0">
                  <span className="block leading-5">{item.label}</span>
                  <span
                    className={cn(
                      "block truncate text-xs font-normal",
                      isActive ? "text-slate-300" : "text-slate-400"
                    )}
                  >
                    {item.description}
                  </span>
                </span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto space-y-3 border-t p-4">
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs">
            <div className="flex items-center gap-2 font-semibold text-emerald-900">
              <ClipboardCheck className="h-4 w-4" />
              Operational Mode
            </div>
            <div className="mt-1 text-emerald-700">
              Monitoring supplier risk, RFQs, and compliance signals.
            </div>
          </div>

          <div className="rounded-lg border border-violet-200 bg-violet-50 p-3 text-xs text-violet-900">
            <div className="font-semibold">AMD ROCm + vLLM</div>
            <div className="mt-1 text-violet-700">
              Agent reasoning badges appear where AI inference is used.
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}