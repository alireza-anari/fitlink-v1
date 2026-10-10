"""Cleanup has no implicit destructive authority."""


def cleanup_asset(
    asset_uuid,
    expected_version,
    policy_uuid,
    at,
    *,
    subject_validator=None,
    hold_validator=None,
    in_use_validator=None,
    store=None,
):
    # Closed boundary until reservation/deletion behavior has observed hosted RED.
    return "denied"
