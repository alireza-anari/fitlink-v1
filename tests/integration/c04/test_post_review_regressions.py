"""Behavioral regressions for the independent Task7 security/correctness review."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from uuid import uuid4

import pytest
from django.db import DatabaseError, transaction
from django.utils import timezone

from apps.assets.public_copies import read_public_copy
from apps.assets.public_storage import PublicationObjectStore
from apps.governance.moderation_contracts import PublicReportTarget
from apps.governance.moderation_models import PublicContentReport
from apps.professionals.post_contracts import PostImageInput, PostInput
from apps.professionals.post_models import EducationalPost, PostImageBinding
from config.use_cases import public_content as content
from config.use_cases import public_media
from tests.integration.c03.profile_helpers import in_connection, make_actor
from tests.integration.c04.copy_helpers import process
from tests.integration.c04.post_helpers import (
    case_step,
    draft,
    image,
    moderator,
    pending_post,
    published,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def assigned(settings, subject, target):
    reporter = make_actor("+989155557020")
    receipt = content.report_public_content(
        reporter.actor, target, "privacy", uuid4(), timezone.now()
    )
    case = PublicContentReport.objects.get(pk=receipt.receipt_id).case
    staff = moderator(settings, case.id)
    result = content.claim_public_moderation(
        staff.actor,
        case.id,
        case.version,
        staff.step,
        "staff_assigned",
        uuid4(),
        timezone.now(),
    )
    return case, staff, result, reporter


def decision(staff, case, version, action):
    reason = {
        "hide": "security_restriction",
        "restore": "restriction_removed",
        "dismiss": "case_conflict",
    }[action]
    return content.decide_public_moderation(
        staff.actor,
        case.id,
        version,
        action,
        staff.step,
        reason,
        uuid4(),
        timezone.now(),
    )


@pytest.mark.parametrize("target_kind", ["profile", "post"])
def test_hide_reconciliation_then_restore_preserves_confirmed_release(
    corpus, settings, target_kind
):
    subject, _ = corpus()
    post, _, _, store, copy = published(subject)
    target = PublicReportTarget(
        target_kind, subject.profile.id if target_kind == "profile" else post.id
    )
    case, staff, claimed, _ = assigned(settings, subject, target)
    hidden = decision(staff, case, claimed.version, "hide")
    assert content.public_post(post.id, timezone.now()) is None
    assert (
        public_media.reconcile_public_media(timezone.now() + timedelta(minutes=1), 100)
        >= 1
    )
    copy.refresh_from_db()
    assert copy.state == "ready", (
        "Temporary moderation must not retire unchanged release bytes"
    )
    decision(staff, case, hidden.version, "restore")
    assert content.public_post(post.id, timezone.now()) is not None
    assert read_public_copy(
        copy.id,
        timezone.now(),
        authorize=public_media.validate_public_copy_read,
        publication_store=PublicationObjectStore(store),
    ).content.startswith(b"\x89PNG")


def test_withdraw_after_write_is_discovered_and_erased_by_installed_reconciler(
    corpus, monkeypatch
):
    import apps.assets.public_storage as storage
    from tests.integration.c03.test_asset_holds import policy

    subject, _ = corpus()
    post, assets, derivatives, store, copies, jobs = pending_post(subject)
    rule = policy(subject, assets[0])

    def withdraw():
        row = EducationalPost.objects.get(pk=post.id)
        content.withdraw_post(
            subject.actor, row.id, row.version, uuid4(), timezone.now()
        )

    store.after_write = withdraw
    assert process(store, jobs[0]).status == "denied"
    attempt = copies[0].attempts.get(generation=1)
    key = attempt.key
    assert key in store.objects and content.public_post(post.id, timezone.now()) is None
    monkeypatch.setattr(
        storage, "get_publication_store", lambda: PublicationObjectStore(store)
    )
    later = attempt.lease_until + timedelta(seconds=2)
    # Use installed discovery, not a hand-picked copy lifetime call.
    public_media.scan_due_public_copies(later, 100)
    assert public_media.reconcile_public_media(later, 100) >= 1
    copies[0].refresh_from_db()
    assert copies[0].state in {"revoked", "deletion_pending", "deleted"}
    public_media.reconcile_public_media(later + timedelta(minutes=1), 100)
    assert key not in store.objects
    assert derivatives[0].key in store.objects
    assert rule.purpose == "educational_image"


def test_immutable_scanned_copy_and_post_have_consistent_read_lifetime(corpus):
    subject, _ = corpus()
    post, _, _, store, copy = published(subject)
    future = timezone.now() + timedelta(hours=2)
    image_read = read_public_copy(
        copy.id,
        future,
        authorize=public_media.validate_public_copy_read,
        publication_store=PublicationObjectStore(store),
    )
    assert image_read.content.startswith(b"\x89PNG")
    assert content.public_post(post.id, future) is not None


def test_restore_deleted_generation_uses_fresh_scan_and_new_object(
    corpus, settings, monkeypatch
):
    import apps.assets.public_storage as storage
    from tests.integration.c03.test_asset_holds import policy

    subject, _ = corpus()
    post, asset, derivative, store, copy = published(subject)
    case, staff, claimed, _ = assigned(
        settings, subject, PublicReportTarget("post", post.id)
    )
    hidden = decision(staff, case, claimed.version, "hide")
    # Simulate an inventoried generation retired by the historical hide defect.
    copy.refresh_from_db()
    copy.state = "revoked"
    copy.revoked_at = timezone.now()
    copy.updated_at = copy.revoked_at
    copy.version += 1
    copy.save()
    old = copy.attempts.get(generation=1)
    rule = policy(subject, asset)
    wrapped = PublicationObjectStore(store)
    assert (
        public_media.cleanup_public_copy(
            copy.id,
            1,
            rule.id,
            timezone.now() + timedelta(seconds=2),
            publication_store=wrapped,
        )
        == "deleted"
    )
    assert old.key not in store.objects and derivative.key in store.objects
    decision(staff, case, hidden.version, "restore")
    assert content.public_post(post.id, timezone.now()) is None
    monkeypatch.setattr(storage, "get_publication_store", lambda: wrapped)
    later = timezone.now() + timedelta(minutes=1)
    assert public_media.reconcile_public_media(later, 100) >= 1
    copy.refresh_from_db()
    assert copy.generation == 2 and copy.state == "pending"
    queued = []
    from apps.assets.public_copies import scan_due_public_copies

    assert (
        scan_due_public_copies(
            later,
            100,
            authorize=public_media.validate_release,
            enqueue=lambda *args: queued.append(args),
        )
        == 1
    )
    assert content.public_post(post.id, timezone.now()) is None
    assert process(store, queued[0], at=later).status == "ready"
    copy.refresh_from_db()
    assert (
        copy.attempts.get(generation=2).key != old.key and old.key not in store.objects
    )
    assert content.public_post(post.id, later) is not None


@pytest.mark.parametrize("superseded", [False, True])
def test_saved_revision_image_membership_is_sealed_against_bulk_append(
    corpus, superseded
):
    subject, _ = corpus()
    post = draft(subject)
    first, _, _ = image(subject, post)
    other, _, _ = image(subject, post)
    post = content.save_post(
        subject.actor,
        post.id,
        PostInput("آموزش", (PostImageInput(first.id, "نخست"),)),
        post.version,
        uuid4(),
        timezone.now(),
    )
    revision = post.revision_id
    if superseded:
        content.save_post(
            subject.actor,
            post.id,
            PostInput("تازه"),
            post.version,
            uuid4(),
            timezone.now(),
        )
    with pytest.raises(DatabaseError), transaction.atomic():
        PostImageBinding.objects.bulk_create(
            [
                PostImageBinding(
                    revision_id=revision,
                    asset=other,
                    position=2,
                    alt="اضافه",
                    asset_version=other.version,
                    processing_version=other.processing_version,
                )
            ]
        )
    assert PostImageBinding.objects.filter(revision_id=revision).count() == 1


def test_assigned_review_binds_reported_revision_and_excludes_private_evidence(
    corpus, settings
):
    subject, _ = corpus()
    post, _, _, store, copy = published(subject)
    case, staff, claimed, reporter = assigned(
        settings, subject, PublicReportTarget("post", post.id)
    )
    hidden = decision(staff, case, claimed.version, "hide")
    view = content.read_public_moderation(
        staff.actor, case.id, staff.step, "security_restriction", timezone.now()
    )
    assert set(view.__dataclass_fields__) == {
        "id",
        "version",
        "state",
        "target",
        "revision_uuid",
        "reasons",
        "content_json",
    }
    assert view.target == PublicReportTarget("post", post.id)
    assert view.revision_uuid == case.revision_uuid and view.reasons == ("privacy",)
    assert set(view.content) == {"text", "images"} and view.content["text"] == "آموزش"
    assert set(view.content["images"][0]) == {"copy_uuid", "alt"}
    assert view.version == hidden.version
    media = content.read_public_moderation_media(
        staff.actor,
        case.id,
        copy.id,
        staff.step,
        "security_restriction",
        timezone.now(),
        publication_store=PublicationObjectStore(store),
    )
    assert media.content.startswith(b"\x89PNG") and media.asset_uuid == copy.id
    _, _, _, _, other_copy = published(subject)
    before = len(store.reads)
    with pytest.raises((PermissionError, LookupError)):
        content.read_public_moderation_media(
            staff.actor,
            case.id,
            other_copy.id,
            staff.step,
            "security_restriction",
            timezone.now(),
            publication_store=PublicationObjectStore(store),
        )
    assert len(store.reads) == before
    for actor, step in [
        (reporter.actor, staff.step),
        (subject.actor, staff.step),
        (staff.actor, case_step(staff, uuid4())),
    ]:
        with pytest.raises((PermissionError, LookupError)):
            content.read_public_moderation(
                actor, case.id, step, "security_restriction", timezone.now()
            )
    row = EducationalPost.objects.get(pk=post.id)
    content.save_post(
        subject.actor,
        row.id,
        PostInput("PRIVATE_UNCONFIRMED_SENTINEL"),
        row.version,
        uuid4(),
        timezone.now(),
    )
    changed = content.read_public_moderation(
        staff.actor, case.id, staff.step, "security_restriction", timezone.now()
    )
    assert changed.content is None and changed.revision_uuid == case.revision_uuid
    with pytest.raises((PermissionError, LookupError)):
        content.read_public_moderation_media(
            staff.actor,
            case.id,
            copy.id,
            staff.step,
            "security_restriction",
            timezone.now(),
            publication_store=PublicationObjectStore(store),
        )


def test_moderation_queue_has_real_keyset_pagination_and_case_scoped_reads(
    corpus, settings
):
    subject, _ = corpus()
    reporter = make_actor("+989155557020")
    cases = []
    for _ in range(3):
        post, *_ = published(subject)
        report = content.report_public_content(
            reporter.actor,
            PublicReportTarget("post", post.id),
            "unsafe",
            uuid4(),
            timezone.now(),
        )
        cases.append(PublicContentReport.objects.get(pk=report.receipt_id).case_id)
    staff = moderator(settings, None)
    first = content.moderation_queue(
        staff.actor, staff.step, "staff_assigned", timezone.now(), limit=2
    )
    second = content.moderation_queue(
        staff.actor,
        staff.step,
        "staff_assigned",
        timezone.now(),
        limit=2,
        cursor=first.cursor,
    )
    assert len(first.cases) == 2 and first.cursor is not None
    assert len(second.cases) == 1 and second.cursor is None
    assert {v.id for v in first.cases + second.cases} == set(cases)
    with pytest.raises((PermissionError, LookupError)):
        content.claim_public_moderation(
            staff.actor,
            cases[0],
            1,
            staff.step,
            "staff_assigned",
            uuid4(),
            timezone.now(),
        )
    step = case_step(staff, cases[0])
    claimed = content.claim_public_moderation(
        staff.actor, cases[0], 1, step, "staff_assigned", uuid4(), timezone.now()
    )
    assert (
        content.read_public_moderation(
            staff.actor, cases[0], step, "staff_assigned", timezone.now()
        ).id
        == claimed.id
    )
    from apps.governance.staff_models import StaffStepUpGrant

    StaffStepUpGrant.objects.filter(pk=step).update(
        verified_at=timezone.now() - timedelta(minutes=10),
        expires_at=timezone.now() - timedelta(minutes=9),
    )
    with pytest.raises((PermissionError, LookupError)):
        content.read_public_moderation(
            staff.actor, cases[0], step, "staff_assigned", timezone.now()
        )


def test_case_media_rechecks_capability_after_buffered_io(corpus, settings):
    subject, _ = corpus()
    post, _, _, store, copy = published(subject)
    case, staff, claimed, _ = assigned(
        settings, subject, PublicReportTarget("post", post.id)
    )
    decision(staff, case, claimed.version, "hide")
    original = store.read_limited

    def revoke(key, maximum):
        body = original(key, maximum)
        staff.grant.revoked_at = timezone.now()
        staff.grant.save(update_fields=["revoked_at"])
        return body

    store.read_limited = revoke
    with pytest.raises((PermissionError, LookupError)):
        content.read_public_moderation_media(
            staff.actor,
            case.id,
            copy.id,
            staff.step,
            "security_restriction",
            timezone.now(),
            publication_store=PublicationObjectStore(store),
        )


def test_competing_moderator_claims_have_one_winner(corpus, settings):
    subject, _ = corpus()
    reporter = make_actor("+989155557020")
    report = content.report_public_content(
        reporter.actor,
        PublicReportTarget("profile", subject.profile.id),
        "unsafe",
        uuid4(),
        timezone.now(),
    )
    case = PublicContentReport.objects.get(pk=report.receipt_id).case
    one = moderator(settings, case.id)
    two = moderator(settings, case.id, phone="+989155557021", issuer=one.issuer)
    barrier = Barrier(2)

    def claim(staff):
        barrier.wait(timeout=10)
        try:
            content.claim_public_moderation(
                staff.actor,
                case.id,
                1,
                staff.step,
                "staff_assigned",
                uuid4(),
                timezone.now(),
            )
            return True
        except (ValueError, PermissionError):
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(in_connection, lambda s=s: claim(s)) for s in (one, two)]
        assert sum(j.result(timeout=25) for j in jobs) == 1
    case.refresh_from_db()
    assert (
        case.assigned_staff_id in {one.user.pk, two.user.pk}
        and case.history.count() == 1
    )


def test_concurrent_final_report_quota_has_one_winner(corpus):
    subject, _ = corpus()
    reporter = make_actor("+989155557020")
    targets = []
    for index in range(6):
        post, *_ = published(subject)
        target = PublicReportTarget("post", post.id)
        if index < 4:
            content.report_public_content(
                reporter.actor, target, "unsafe", uuid4(), timezone.now()
            )
        else:
            targets.append(target)
    barrier = Barrier(2)

    def report(target):
        barrier.wait(timeout=10)
        try:
            content.report_public_content(
                reporter.actor, target, "unsafe", uuid4(), timezone.now()
            )
            return True
        except PermissionError:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(in_connection, lambda t=t: report(t)) for t in targets]
        assert sum(j.result(timeout=25) for j in jobs) == 1
    assert PublicContentReport.objects.filter(reporter=reporter.user).count() == 5


@pytest.mark.parametrize("order", ["hide_before_release", "copy_before_hide"])
def test_parent_hide_linearizes_against_late_post_copy(corpus, settings, order):
    subject, _ = corpus()
    case, staff, claimed, _ = assigned(
        settings, subject, PublicReportTarget("profile", subject.profile.id)
    )
    post, _, _, store, copies, jobs = pending_post(subject)

    def hide():
        decision(staff, case, claimed.version, "hide")

    if order == "hide_before_release":
        store.after_write = hide
        assert process(store, jobs[0]).status == "denied"
    else:
        assert process(store, jobs[0]).status == "ready"
        hide()
    assert content.public_post(post.id, timezone.now()) is None


def test_four_image_post_never_activates_with_only_three_outputs(corpus):
    subject, _ = corpus()
    post, _, _, store, copies, jobs = pending_post(subject, 4)
    for job in jobs[:3]:
        assert process(store, job).status == "ready"
        assert content.public_post(post.id, timezone.now()) is None
    assert process(store, jobs[3]).status == "ready"
    assert len(content.public_post(post.id, timezone.now()).images) == 4


def test_withdrawal_during_buffered_post_release_wins(corpus):
    subject, _ = corpus()
    post, *_ = published(subject)

    def release(dto):
        row = EducationalPost.objects.get(pk=post.id)
        content.withdraw_post(
            subject.actor, row.id, row.version, uuid4(), timezone.now()
        )
        return dto

    assert content.public_post(post.id, timezone.now(), release=release) is None


@pytest.mark.parametrize(
    "order", ["withdraw_before_restore", "restore_before_withdraw"]
)
def test_restore_after_owner_withdrawal_does_not_republish(corpus, settings, order):
    subject, _ = corpus()
    post, *_ = published(subject)
    case, staff, claimed, _ = assigned(
        settings, subject, PublicReportTarget("post", post.id)
    )
    hidden = decision(staff, case, claimed.version, "hide")
    if order == "restore_before_withdraw":
        decision(staff, case, hidden.version, "restore")
    row = EducationalPost.objects.get(pk=post.id)
    content.withdraw_post(subject.actor, row.id, row.version, uuid4(), timezone.now())
    if order == "withdraw_before_restore":
        decision(staff, case, hidden.version, "restore")
    assert content.public_post(post.id, timezone.now()) is None


@pytest.mark.parametrize("order", ["hide_before_confirm", "confirm_before_hide"])
def test_parent_hide_linearizes_against_post_confirmation(corpus, settings, order):
    subject, _ = corpus()
    case, staff, claimed, _ = assigned(
        settings, subject, PublicReportTarget("profile", subject.profile.id)
    )
    post = draft(subject)
    asset, _, _ = image(subject, post)
    post = content.save_post(
        subject.actor,
        post.id,
        PostInput("آموزش", (PostImageInput(asset.id, "شرح"),)),
        post.version,
        uuid4(),
        timezone.now(),
    )
    if order == "confirm_before_hide":
        content.publish_post(
            subject.actor, post.id, True, post.version, uuid4(), timezone.now()
        )
        decision(staff, case, claimed.version, "hide")
    else:
        decision(staff, case, claimed.version, "hide")
        with pytest.raises((ValueError, LookupError, PermissionError)):
            content.publish_post(
                subject.actor, post.id, True, post.version, uuid4(), timezone.now()
            )
    assert content.public_post(post.id, timezone.now()) is None


@pytest.mark.parametrize("target_kind", ["profile", "post"])
@pytest.mark.parametrize("during_io", [False, True])
def test_assigned_media_denies_stale_derivative_binding(
    corpus, settings, target_kind, during_io
):
    if target_kind == "post":
        subject, _ = corpus()
        post, _, derivative, store, copy = published(subject)
        target_uuid = post.id
    else:
        from tests.integration.c04.copy_helpers import copy_model, pending

        subject, _, _, derivative, store, dto, job = pending(settings)
        assert process(store, job).status == "ready"
        copy = copy_model().objects.get(pk=dto.id)
        target_uuid = subject.profile.id
    case, staff, claimed, _ = assigned(
        settings, subject, PublicReportTarget(target_kind, target_uuid)
    )
    decision(staff, case, claimed.version, "hide")

    def mutate():
        derivative.version += 1
        derivative.save(update_fields=["version"])

    if during_io:
        original = store.read_limited

        def change_after_read(key, maximum):
            body = original(key, maximum)
            mutate()
            return body

        store.read_limited = change_after_read
    else:
        mutate()
        view = content.read_public_moderation(
            staff.actor, case.id, staff.step, "security_restriction", timezone.now()
        )
        assert view.content is None
    before = len(store.reads)
    with pytest.raises((PermissionError, LookupError)):
        content.read_public_moderation_media(
            staff.actor,
            case.id,
            copy.id,
            staff.step,
            "security_restriction",
            timezone.now(),
            publication_store=PublicationObjectStore(store),
        )
    assert len(store.reads) == before + int(during_io)
