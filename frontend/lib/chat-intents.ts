import { supplierProfiles } from "@/lib/operational-data";

export type ChatIntent =
  | "Risk explanation"
  | "Supplier alternatives"
  | "Mitigation planning"
  | "RFQ review"
  | "Compliance review"
  | "General investigation";

export const investigationPrompts = [
  "Why is SUP-CN-001 risky?",
  "Find safer alternatives for the China supplier.",
  "Show RFQs waiting for approval.",
  "Check compliance issues.",
  "Generate a mitigation plan.",
];

export function detectSupplierId(prompt: string): string | null {
  const upper = prompt.toUpperCase();

  const explicitSupplier = supplierProfiles.find((supplier) =>
    upper.includes(supplier.id)
  );

  if (explicitSupplier) {
    return explicitSupplier.id;
  }

  if (upper.includes("CHINA") || upper.includes("SEMICONDUCTOR")) {
    return "SUP-CN-001";
  }

  if (upper.includes("GERMAN") || upper.includes("GERMANY")) {
    return "SUP-DE-001";
  }

  if (upper.includes("US ") || upper.includes("UNITED STATES")) {
    return "SUP-US-001";
  }

  if (upper.includes("INDIA") || upper.includes("INDIAN")) {
    return "SUP-IN-001";
  }

  if (upper.includes("IRAN") || upper.includes("COMPLIANCE")) {
    return "SUP-IR-001";
  }

  return null;
}

export function detectChatIntent(prompt: string): ChatIntent {
  const lower = prompt.toLowerCase();

  if (lower.includes("rfq") || lower.includes("quote") || lower.includes("approval")) {
    return "RFQ review";
  }

  if (
    lower.includes("compliance") ||
    lower.includes("sanction") ||
    lower.includes("trade") ||
    lower.includes("blocked")
  ) {
    return "Compliance review";
  }

  if (
    lower.includes("alternative") ||
    lower.includes("safer") ||
    lower.includes("backup")
  ) {
    return "Supplier alternatives";
  }

  if (lower.includes("mitigation") || lower.includes("plan")) {
    return "Mitigation planning";
  }

  if (lower.includes("why") || lower.includes("risk")) {
    return "Risk explanation";
  }

  return "General investigation";
}

export function getIntentNextAction(intent: ChatIntent) {
  switch (intent) {
    case "Risk explanation":
      return "Run risk analysis and explain operational impact";
    case "Supplier alternatives":
      return "Compare safer suppliers and prepare mitigation options";
    case "Mitigation planning":
      return "Generate mitigation plan and sourcing recommendation";
    case "RFQ review":
      return "Review generated RFQs and approval blockers";
    case "Compliance review":
      return "Check sanctions, trade controls, and policy blockers";
    default:
      return "Run agent investigation";
  }
}
