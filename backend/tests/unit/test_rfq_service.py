import pytest

from app.schemas.execution import RFQStatus
from app.services.rfq_service import RFQService


@pytest.mark.parametrize(
    ("input_status", "expected"),
    [
        ("pending_approval", RFQStatus.PENDING_APPROVAL),
        ("Pending Approval", RFQStatus.PENDING_APPROVAL),
        ("review-requested", RFQStatus.REVIEW_REQUESTED),
        ("COMPLIANCE_REVIEW", RFQStatus.COMPLIANCE_REVIEW),
    ],
)
def test_rfq_service_accepts_status_filter_aliases(input_status, expected):
    service = RFQService(session=None)  # type: ignore[arg-type]

    assert service._parse_status(input_status) == expected


def test_rfq_service_records_status_names_for_audit():
    service = RFQService(session=None)  # type: ignore[arg-type]

    assert service._status_name(RFQStatus.APPROVED) == "APPROVED"
    assert service._status_name("rejected") == "REJECTED"
