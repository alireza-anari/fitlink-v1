"""Comparison uses server sessions, bounded slots and fresh public readers."""

from uuid import uuid4

import pytest
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest
from django.utils import timezone

from tests.integration.c04.selection_helpers import athlete, change, require, scope

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def visitor():
    from types import SimpleNamespace

    request = HttpRequest()
    request.session = SessionStore()
    return SimpleNamespace(request=request)


def test_fourth_comparison_rejected_409(corpus):
    person = athlete()
    targets = [corpus()[0] for _ in range(4)]
    initial = require("read_comparison")(scope(person), timezone.now())
    assert initial.items == ()
    result = initial
    for target in targets[:3]:
        result = change(person, "add", target.profile.id, result.version)
    assert len(result.items) == 3
    from apps.marketplace.selection_contracts import SelectionConflict

    with pytest.raises(SelectionConflict):
        change(person, "add", targets[3].profile.id, result.version)
    assert len(require("read_comparison")(scope(person), timezone.now()).items) == 3


def test_duplicate_ids_and_receipts_never_consume_slots(corpus):
    person = athlete()
    target, _ = corpus()
    initial = require("read_comparison")(scope(person), timezone.now())
    operation = uuid4()
    first = change(person, "add", target.profile.id, initial.version, operation)
    replay = change(person, "add", target.profile.id, initial.version, operation)
    assert replay == first and len(first.items) == 1
    second = change(person, "add", target.profile.id, first.version)
    assert len(second.items) == 1


def test_visitor_session_isolation_and_flush_rotates_without_merge(corpus):
    person, other = visitor(), visitor()
    target, _ = corpus()
    old = scope(person)
    first = require("read_comparison")(old, timezone.now())
    change(person, "add", target.profile.id, first.version)
    assert require("read_comparison")(scope(other), timezone.now()).items == ()
    person.request.session.flush()
    assert require("read_comparison")(scope(person), timezone.now()).items == ()
    with pytest.raises(PermissionError):
        require("read_comparison")(old, timezone.now())


def test_authenticated_revoked_session_never_falls_back_to_visitor():
    person = athlete()
    person.user.auth_version += 1
    person.user.save(update_fields=["auth_version"])
    with pytest.raises(PermissionError):
        scope(person)


def test_off_flag_clear_and_hidden_target_revalidation(corpus):
    from apps.governance.flag_models import FeatureFlag

    person = visitor()
    target, _ = corpus()
    first = require("read_comparison")(scope(person), timezone.now())
    selected = change(person, "add", target.profile.id, first.version)
    FeatureFlag.objects.filter(key="marketplace").update(enabled=False)
    current = require("read_comparison")(scope(person), timezone.now())
    assert current.items == () and current.version == selected.version
    assert change(person, "clear", None, current.version).items == ()


def test_session_expiry_during_buffered_read_denies_release(corpus):
    from datetime import timedelta

    from django.contrib.sessions.models import Session

    person = visitor()
    target, _ = corpus()
    selected_scope = scope(person)
    first = require("read_comparison")(selected_scope, timezone.now())
    change(person, "add", target.profile.id, first.version)

    def expire(value):
        assert len(value.items) == 1
        Session.objects.filter(session_key=person.request.session.session_key).update(
            expire_date=timezone.now() - timedelta(seconds=1)
        )
        return value

    with pytest.raises(PermissionError):
        require("read_comparison")(selected_scope, timezone.now(), release=expire)


def test_actual_login_and_account_switch_do_not_merge_visitor_selections(corpus):
    from django.db import transaction

    from apps.accounts.sessions import issue_session
    from apps.governance.audit import append_event

    person = visitor()
    target, _ = corpus()
    old_scope = scope(person)
    first = require("read_comparison")(old_scope, timezone.now())
    change(person, "add", target.profile.id, first.version)
    for phone in ("+989155550006", "+989155550007"):
        owner = athlete(phone)
        with transaction.atomic():
            issue_session(
                person.request, owner.user, "normal", timezone.now(), append_event
            )
        assert require("read_comparison")(scope(person), timezone.now()).items == ()
    with pytest.raises(PermissionError):
        require("read_comparison")(old_scope, timezone.now())
