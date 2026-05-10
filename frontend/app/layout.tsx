import type { Metadata } from "next";
import "./globals.css";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { QueryProvider } from "@/lib/query-client";
import { cn } from "@/lib/utils";

export const metadata: Metadata = {
  title: "SupplyChain Guardian",
  description: "AI-powered supply chain risk management platform",
  icons: {
    icon: "/icon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased"
        )}
      >
        <QueryProvider>
          <DashboardShell>{children}</DashboardShell>
        </QueryProvider>
      </body>
    </html>
  );
}
