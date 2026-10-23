"""A staff flag or report never grants moderation or private-evidence access."""

from uuid import uuid4

import pytest
from django.utils import timezone

from tests.integration.c03.profile_helpers import make_actor
from tests.integration.c04.post_helpers import command

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_staff_flag_cannot_claim_public_moderation(corpus):
    claim = command("claim_public_moderation")
    staff = make_actor("+989155557002")
    staff.user.is_staff = True
    staff.user.save(update_fields=["is_staff"])
    with pytest.raises((PermissionError, LookupError)):
        claim(
            staff.actor, uuid4(), 1, uuid4(), "security_review", uuid4(), timezone.now()
        )


def test_duplicate_reports_are_bounded_and_receipt_has_no_content(corpus):
    report = command("report_public_content")
    subject, _ = corpus()
    reporter = make_actor("+989155557003")
    from apps.governance.moderation_contracts import PublicReportTarget

    target = PublicReportTarget("profile", subject.profile.id)
    one = report(reporter.actor, target, "privacy", uuid4(), timezone.now())
    two = report(reporter.actor, target, "privacy", uuid4(), timezone.now())
    assert one == two
    assert set(one.__dataclass_fields__) == {"receipt_id"}


@pytest.mark.parametrize("reason", ["private notes", "<script>", "", None])
def test_report_free_text_and_unknown_reason_denied(reason):
    report = command("report_public_content")
    actor = make_actor("+989155557004")
    from apps.governance.moderation_contracts import PublicReportTarget

    with pytest.raises(ValueError):
        report(
            actor.actor,
            PublicReportTarget("profile", uuid4()),
            reason,
            uuid4(),
            timezone.now(),
        )
