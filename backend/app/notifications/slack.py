from app.schemas.execution import RFQDocument
from app.schemas.mitigation import MitigationPlan


def build_approval_slack_message(
    rfqs: list[RFQDocument],
    gate_result: dict,
    mitigation_plan: MitigationPlan,
) -> dict:
    """
    Build Slack Block Kit approval message.

    MVP only builds the message payload.
    Actual Slack dispatch will be wired later.
    """

    top = mitigation_plan.recommended_options[0]

    issues_text = "\n".join(
        f"• {issue}"
        for issue in gate_result.get("issues", [])
    ) or "No issues detected"

    first_rfq_id = rfqs[0].rfq_id if rfqs else "unknown"

    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "*RFQ Approval Required*\n"
                        f"Original Supplier: `{mitigation_plan.original_supplier_id}`\n"
                        f"Risk Score: `{mitigation_plan.risk_score}/100`"
                    ),
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"Top Recommendation: `{top.supplier_id}`\n"
                        f"Cost Delta: `{top.cost_delta_pct:+.1f}%`\n"
                        f"Lead Time Delta: `{top.lead_time_delta_days:+d} days`\n"
                        f"Residual Risk: `{top.residual_risk_score}/100`"
                    ),
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Approval Flags:*\n{issues_text}",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Approve",
                        },
                        "style": "primary",
                        "url": f"https://scg.internal/approve/{first_rfq_id}",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Reject",
                        },
                        "style": "danger",
                        "url": f"https://scg.internal/reject/{first_rfq_id}",
                    },
                ],
            },
        ]
    }


async def post_approval_request(
    channel: str,
    message: dict,
) -> dict:
    """
    MVP placeholder for Slack delivery.
    """

    return {
        "sent": False,
        "simulated": True,
        "channel": channel,
        "message": message,
    }