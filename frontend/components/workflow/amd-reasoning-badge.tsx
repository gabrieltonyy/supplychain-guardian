import { Badge } from "@/components/ui/badge";
import { getReasoningSourceBadge } from "@/lib/utils";

type AMDReasoningBadgeProps = {
  label: string;
  source?: string | null;
};

export function AMDReasoningBadge({ label, source }: AMDReasoningBadgeProps) {
  const badge = getReasoningSourceBadge(source);

  return (
    <Badge className={`${badge.color} border`}>
      <span className="font-medium">{label}:</span>
      <span className="ml-1">{badge.label}</span>
    </Badge>
  );
}
