from datetime import datetime, UTC

from app.notifications.email import send_rfq_email
from app.schemas.execution import RFQDocument, RFQStatus


async def dispatch_rfq(
    rfq: RFQDocument,
    simulated: bool = True,
) -> dict:
    """
    Dispatch RFQ via email.

    MVP:
    - renders email,
    - simulates dispatch,
    - returns dispatch log entry.
    """

    result = await send_rfq_email(
        rfq=rfq,
        simulated=simulated,
    )

    dispatch_entry = {
        "rfq_id": rfq.rfq_id,
        "channel": "email" if not simulated else "simulated",
        "sent_at": datetime.now(UTC).isoformat(),
        "status": (
            RFQStatus.DISPATCHED.value
            if not simulated
            else "simulated"
        ),
        "recipient": rfq.supplier_email,
        "delivery_result": result,
    }

    return dispatch_entry