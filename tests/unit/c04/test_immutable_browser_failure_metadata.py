"""Browser failure metadata never exports locators, payloads or private paths."""

import importlib
import json

import pytest

pytestmark = pytest.mark.unit
KNOWN = "tests/e2e/c03/test_staff_verification.py"


def classifier():
    observer = importlib.import_module("docker.c04_baseline_runtime")
    function = getattr(observer, "classify_browser_private_log", None)
    assert callable(function), "Missing finite immutable-browser failure metadata"
    return function


def test_browser_failure_retains_only_known_source_and_finite_operation():
    function = classifier()
    text = (
        "Error: Locator.click: net::ERR_ABORTED PRIVATE_PAYLOAD\n"
        f"{KNOWN}:182: in test_decision_reload_single_effect\n"
        "private/customer-phone.py:123: PRIVATE_PAYLOAD\n"
        "https://private.invalid/download?token=PRIVATE_PAYLOAD\n"
    )
    result = function(text, {KNOWN})
    assert result == {
        "error_classes": ["Error"],
        "locations": [{"file": KNOWN, "line": 182}],
        "net_codes": ["ERR_ABORTED"],
        "operations": ["Locator.click"],
    }
    assert "PRIVATE_PAYLOAD" not in json.dumps(result)
    assert "private.invalid" not in json.dumps(result)


def test_browser_failure_locations_are_bounded_and_unknown_text_stays_private():
    function = classifier()
    text = "\n".join(f"{KNOWN}:{line}: PRIVATE_PAYLOAD" for line in range(1, 501))
    result = function(text, {KNOWN})
    assert len(result["locations"]) == 12
    assert len(json.dumps(result)) < 4096
    assert "PRIVATE_PAYLOAD" not in json.dumps(result)
    assert function("PRIVATE_PAYLOAD unknown-private-file.py:12", {KNOWN}) == {
        "error_classes": [],
        "locations": [],
        "net_codes": [],
        "operations": [],
    }
