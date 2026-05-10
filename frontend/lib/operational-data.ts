import type { RiskLevel } from "@/lib/api-types";

export type Severity = "Critical" | "High" | "Medium" | "Low";

export type SupplierProfile = {
  id: string;
  name: string;
  region: string;
  category: string;
  exposure: string;
  severity: Severity;
  incident: string;
  impact: string;
  businessRisk: string;
  recommendedAction: string;
  operationalImpact: string[];
};

export const supplierProfiles: SupplierProfile[] = [
  {
    id: "SUP-CN-001",
    name: "China Electronics",
    region: "China",
    category: "Semiconductors",
    exposure: "$1.4M",
    severity: "Critical",
    incident: "Semiconductor supply disruption",
    impact: "12-day delivery delay",
    businessRisk: "Port delays and component shortage exposure",
    recommendedAction: "Switch 40% to SUP-DE-001 and approve emergency RFQ",
    operationalImpact: [
      "Inventory depletion risk within 5 days",
      "Manufacturing delays likely for semiconductor-dependent products",
      "Potential SLA breach for downstream customers",
    ],
  },
  {
    id: "SUP-DE-001",
    name: "German Auto Parts",
    region: "Germany",
    category: "Automotive Parts",
    exposure: "$620K",
    severity: "Low",
    incident: "Backup supplier review",
    impact: "Stable backup capacity",
    businessRisk: "Stable supplier used as a backup option",
    recommendedAction: "Keep as preferred mitigation option",
    operationalImpact: [
      "Available for partial sourcing redistribution",
      "Low operational risk detected",
      "Strong mitigation candidate",
    ],
  },
  {
    id: "SUP-US-001",
    name: "US Tech Components",
    region: "United States",
    category: "Tech Components",
    exposure: "$780K",
    severity: "Medium",
    incident: "High-cost alternate review",
    impact: "Short lead time, higher cost",
    businessRisk: "Shorter lead time with higher unit cost",
    recommendedAction: "Compare against EU backup options",
    operationalImpact: [
      "Useful as urgent fulfillment backup",
      "Margin impact likely if used as primary source",
      "Procurement should compare landed cost before approval",
    ],
  },
  {
    id: "SUP-IN-001",
    name: "Indian Semiconductor",
    region: "India",
    category: "Semiconductors",
    exposure: "$510K",
    severity: "Medium",
    incident: "Lead-time anomaly",
    impact: "6-day delay vs baseline",
    businessRisk: "Lead-time anomaly under observation",
    recommendedAction: "Request delivery update and alternate quotes",
    operationalImpact: [
      "Possible downstream scheduling delays",
      "Inventory replenishment timing uncertainty",
      "Escalation not yet required",
    ],
  },
  {
    id: "SUP-IR-001",
    name: "Iran Raw Materials",
    region: "Iran",
    category: "Raw Materials",
    exposure: "$420K",
    severity: "High",
    incident: "Trade compliance hold",
    impact: "Compliance review required",
    businessRisk: "Compliance and trade-control review required",
    recommendedAction: "Hold execution until compliance officer approval",
    operationalImpact: [
      "Execution blocked by policy controls",
      "Legal/compliance review required",
      "Procurement workflow paused",
    ],
  },
];

export const supplierProfileById = supplierProfiles.reduce<
  Record<string, SupplierProfile>
>((profiles, supplier) => {
  profiles[supplier.id] = supplier;
  return profiles;
}, {});

export const fallbackSupplierProfile: SupplierProfile = {
  id: "UNKNOWN-SUPPLIER",
  name: "Unknown supplier",
  region: "Unknown",
  category: "Unknown",
  exposure: "TBD",
  severity: "Medium",
  incident: "Supplier risk investigation",
  impact: "Assessment available in detail",
  businessRisk: "Operational impact pending review",
  recommendedAction: "Review agent recommendation",
  operationalImpact: ["Operational context not available"],
};

export function getSupplierProfile(supplierId?: string | null): SupplierProfile {
  if (!supplierId) {
    return fallbackSupplierProfile;
  }

  return supplierProfileById[supplierId] ?? {
    ...fallbackSupplierProfile,
    id: supplierId,
    name: supplierId,
  };
}

export function getSeverityClass(severity: Severity | string) {
  switch (severity) {
    case "Critical":
      return "border-red-200 bg-red-50 text-red-700";
    case "High":
      return "border-orange-200 bg-orange-50 text-orange-700";
    case "Medium":
      return "border-amber-200 bg-amber-50 text-amber-700";
    default:
      return "border-emerald-200 bg-emerald-50 text-emerald-700";
  }
}

export function severityFromRiskLevel(level?: RiskLevel | null): Severity {
  switch (level) {
    case "CRITICAL":
      return "Critical";
    case "HIGH":
      return "High";
    case "MEDIUM":
      return "Medium";
    case "LOW":
      return "Low";
    default:
      return "Medium";
  }
}

export const operationalMetrics = [
  {
    label: "Critical Incidents",
    value: "3",
    detail: "Require immediate action",
    href: "/workflows",
    tone: "text-red-600 bg-red-50 border-red-200",
  },
  {
    label: "Pending RFQs",
    value: "12",
    detail: "Awaiting approval",
    href: "/rfqs",
    tone: "text-blue-600 bg-blue-50 border-blue-200",
  },
  {
    label: "Compliance Flags",
    value: "2",
    detail: "Need review",
    href: "/workflows",
    tone: "text-purple-600 bg-purple-50 border-purple-200",
  },
  {
    label: "Estimated Exposure",
    value: "$2.3M",
    detail: "Operational impact",
    href: "/analytics",
    tone: "text-emerald-600 bg-emerald-50 border-emerald-200",
  },
];

export const pendingDecisions = [
  {
    title: "Approve emergency RFQ",
    detail: "3 supplier quotes ready for semiconductor sourcing",
    owner: "Procurement",
    href: "/rfqs",
  },
  {
    title: "Review compliance hold",
    detail: "1 workflow blocked on sanctions review",
    owner: "Compliance",
    href: "/workflows",
  },
  {
    title: "Confirm mitigation plan",
    detail: "Risk agent recommends supplier diversification",
    owner: "Supply Chain Ops",
    href: "/workflows",
  },
];
