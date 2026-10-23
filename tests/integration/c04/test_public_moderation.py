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


@pytest.mark.parametrize("kind", ["profile", "post"])
def test_assigned_capability_hide_restore_only_removes_own_latch(
    corpus, settings, kind
):
    from apps.governance.moderation_contracts import PublicReportTarget
    from apps.governance.moderation_models import PublicContentReport
    from config.use_cases.marketplace import public_professional
    from tests.integration.c04.post_helpers import moderator, published

    subject, _ = corpus()
    identifier = subject.profile.id
    read = public_professional
    if kind == "post":
        post, *_ = published(subject)
        identifier = post.id
        read = command("public_post")
    reporter = make_actor("+989155557012")
    receipt = command("report_public_content")(
        reporter.actor,
        PublicReportTarget(kind, identifier),
        "privacy",
        uuid4(),
        timezone.now(),
    )
    case = PublicContentReport.objects.get(pk=receipt.receipt_id).case
    staff = moderator(settings, case.id)
    claimed = command("claim_public_moderation")(
        staff.actor,
        case.id,
        case.version,
        staff.step,
        "security_review",
        uuid4(),
        timezone.now(),
    )
    with pytest.raises((PermissionError, LookupError, ValueError)):
        command("decide_public_moderation")(
            staff.actor,
            case.id,
            case.version,
            "hide",
            staff.step,
            "security_review",
            uuid4(),
            timezone.now(),
        )
    hidden = command("decide_public_moderation")(
        staff.actor,
        case.id,
        claimed.version,
        "hide",
        staff.step,
        "security_review",
        uuid4(),
        timezone.now(),
    )
    assert read(identifier, timezone.now()) is None
    restored = command("decide_public_moderation")(
        staff.actor,
        case.id,
        hidden.version,
        "restore",
        staff.step,
        "security_review",
        uuid4(),
        timezone.now(),
    )
    assert restored.state == "restored" and read(identifier, timezone.now()) is not None
    staff.grant.revoked_at = timezone.now()
    staff.grant.save(update_fields=["revoked_at"])
    with pytest.raises((PermissionError, LookupError)):
        command("decide_public_moderation")(
            staff.actor,
            case.id,
            restored.version,
            "hide",
            staff.step,
            "security_review",
            uuid4(),
            timezone.now(),
        )


@pytest.mark.parametrize("conflict", ["owner", "reporter"])
def test_owner_and_reporter_cannot_moderate_even_with_capability(
    corpus, settings, conflict
):
    from apps.governance.moderation_contracts import PublicReportTarget
    from apps.governance.moderation_models import PublicContentReport
    from tests.integration.c04.post_helpers import moderator

    subject, _ = corpus()
    reporter = make_actor("+989155557012")
    receipt = command("report_public_content")(
        reporter.actor,
        PublicReportTarget("profile", subject.profile.id),
        "unsafe",
        uuid4(),
        timezone.now(),
    )
    case = PublicContentReport.objects.get(pk=receipt.receipt_id).case
    staff = moderator(
        settings, case.id, person=subject if conflict == "owner" else reporter
    )
    with pytest.raises((PermissionError, LookupError)):
        command("claim_public_moderation")(
            staff.actor,
            case.id,
            case.version,
            staff.step,
            "security_review",
            uuid4(),
            timezone.now(),
        )


def test_report_quota_and_duplicate_are_account_serialized(corpus):
    from apps.governance.moderation_contracts import PublicReportTarget
    from apps.governance.moderation_models import PublicContentReport
    from tests.integration.c04.post_helpers import published

    subject, _ = corpus()
    reporter = make_actor("+989155557012")
    for index in range(6):
        post, *_ = published(subject)
        args = (reporter.actor, PublicReportTarget("post", post.id), "unsafe")
        if index == 5:
            with pytest.raises(PermissionError):
                command("report_public_content")(*args, uuid4(), timezone.now())
        else:
            one = command("report_public_content")(*args, uuid4(), timezone.now())
            assert (
                command("report_public_content")(*args, uuid4(), timezone.now()) == one
            )
    assert PublicContentReport.objects.filter(reporter=reporter.user).count() == 5
