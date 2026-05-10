import { InvestigationAssistant } from "@/components/chat/investigation-assistant";

export default function DemoRunPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-950">
          AI Investigation
        </h1>
        <p className="mt-2 max-w-3xl text-slate-600">
          Ask an operational question, confirm the supplier context, and run the
          agent workflow for risk, mitigation, RFQ, and compliance review.
        </p>
      </div>

      <InvestigationAssistant />
    </div>
  );
}
