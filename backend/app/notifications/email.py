from app.schemas.execution import RFQDocument


def render_rfq_email(
    rfq: RFQDocument,
) -> str:
    """
    Render RFQ email body as simple HTML.

    MVP uses static HTML.
    Later this can move to Jinja templates.
    """

    line_items_html = ""

    for item in rfq.line_items:
        line_items_html += f"""
        <tr>
            <td>{item.sku}</td>
            <td>{item.description}</td>
            <td>{item.quantity}</td>
            <td>{item.unit}</td>
            <td>{item.target_price}</td>
        </tr>
        """

    return f"""
    <html>
        <body>
            <h2>Request for Quotation</h2>

            <p>Dear {rfq.supplier_name},</p>

            <p>
                We are requesting a quotation for the items listed below.
                Please respond before <strong>{rfq.response_deadline}</strong>.
            </p>

            <table border="1" cellspacing="0" cellpadding="6">
                <thead>
                    <tr>
                        <th>SKU</th>
                        <th>Description</th>
                        <th>Quantity</th>
                        <th>Unit</th>
                        <th>Target Price</th>
                    </tr>
                </thead>
                <tbody>
                    {line_items_html}
                </tbody>
            </table>

            <p>
                Delivery destination:
                <strong>{rfq.delivery_destination}</strong>
            </p>

            <p>
                Terms reference:
                <strong>{rfq.terms_ref}</strong>
            </p>

            <p>
                RFQ ID:
                <strong>{rfq.rfq_id}</strong>
            </p>

            <p>Regards,<br/>SupplyChain Guardian Procurement Agent</p>
        </body>
    </html>
    """


async def send_rfq_email(
    rfq: RFQDocument,
    simulated: bool = True,
) -> dict:
    """
    MVP email sender.

    In simulated mode, no real email is sent.
    """

    body = render_rfq_email(rfq)

    if simulated:
        return {
            "sent": False,
            "simulated": True,
            "recipient": rfq.supplier_email,
            "subject": f"RFQ {rfq.rfq_id[:8]} — Urgent Supply Request",
            "body": body,
        }

    # SendGrid integration will be wired later.
    return {
        "sent": False,
        "simulated": False,
        "recipient": rfq.supplier_email,
        "error": "Real email dispatch not configured yet",
    }