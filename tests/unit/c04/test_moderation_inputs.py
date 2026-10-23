"""Reports carry finite public target/reason metadata, never evidence payloads."""

import importlib
import importlib.util
from uuid import uuid4

import pytest


def contracts():
    name = "apps.governance.moderation_contracts"
    assert importlib.util.find_spec(name), "Missing finite moderation contract"
    return importlib.import_module(name)


@pytest.mark.parametrize("kind", ["profile", "post"])
def test_public_report_target_is_only_a_typed_identifier(kind):
    identifier = uuid4()
    target = contracts().PublicReportTarget(kind, identifier)
    assert (target.kind, target.object_uuid) == (kind, identifier)
    assert set(target.__dataclass_fields__) == {"kind", "object_uuid"}


@pytest.mark.parametrize(
    "kind,identifier",
    [
        ("asset", uuid4()),
        ("message", uuid4()),
        ("review", uuid4()),
        ("profile", "forged"),
        (None, uuid4()),
    ],
)
def test_private_or_future_report_targets_denied(kind, identifier):
    with pytest.raises(ValueError):
        contracts().PublicReportTarget(kind, identifier)


@pytest.mark.parametrize("reason", ["privacy", "unsafe", "misleading", "other"])
def test_finite_reporting_reasons_admitted(reason):
    contracts().validate_report_command(
        contracts().PublicReportTarget("post", uuid4()), reason, uuid4()
    )


@pytest.mark.parametrize(
    "reason", ["arbitrary private report text", "", None, {"evidence": "private"}]
)
def test_arbitrary_reporting_payload_denied(reason):
    with pytest.raises(ValueError):
        contracts().validate_report_command(
            contracts().PublicReportTarget("profile", uuid4()), reason, uuid4()
        )


@pytest.mark.parametrize("action", ["hide", "dismiss", "restore"])
def test_only_content_moderation_decisions_admitted(action):
    contracts().validate_decision_command(uuid4(), 1, action, uuid4(), uuid4())


@pytest.mark.parametrize(
    "version,action",
    [(True, "hide"), (0, "hide"), (1, "rewrite"), (1, "suspend"), (1, "publish")],
)
def test_moderation_cannot_impersonate_or_expand_to_account_restriction(
    version, action
):
    with pytest.raises(ValueError):
        contracts().validate_decision_command(
            uuid4(), version, action, uuid4(), uuid4()
        )
