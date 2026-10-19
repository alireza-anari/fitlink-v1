"""Immutable baseline diagnostics disclose finite categories, never private logs."""

import importlib


def module():
    name = "docker.c04_baseline_runtime"
    assert importlib.util.find_spec(name), "Missing immutable baseline outer observer"
    return importlib.import_module(name)


def test_npm_http_error_is_classified_without_private_output():
    result = module().classify_private_log(
        "npm error code E503\nnpm error private-token private-phone\n"
    )
    assert result == {"npm_codes": ["E503"], "categories": ["npm_failure"]}


def test_unknown_error_stays_unknown_and_categories_are_bounded():
    result = module().classify_private_log(
        "private arbitrary exception E503\n"
        "npm error code PRIVATE_TOKEN\n"
        "npm error code ECONNRESET\nnpm ERR! code EAI_AGAIN\n"
        "Failed to download dependency\n"
    )
    assert result == {
        "npm_codes": ["EAI_AGAIN", "ECONNRESET"],
        "categories": ["dependency_download", "npm_failure"],
    }
    assert module().classify_private_log("private E503") == {
        "npm_codes": [],
        "categories": [],
    }


def test_outer_observer_preserves_exact_exit_and_command(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from unittest.mock import Mock

    observer = module()
    baseline = tmp_path / ".runtime/c03"
    private = baseline / ".runtime/task14-private"
    private.mkdir(parents=True)
    (private / "exact_original_c02.log").write_text("npm error code E503\nPRIVATE")
    verify = Mock(return_value="verified-tree")
    run = Mock(return_value=SimpleNamespace(returncode=17))
    monkeypatch.setattr(observer, "verify_baseline", verify)
    monkeypatch.setattr(observer.subprocess, "run", run)
    assert observer.run(tmp_path) == 17
    run.assert_called_once_with(["sh", "docker/verify_c03.sh"], cwd=baseline)
    assert verify.call_count == 1
    assert list((tmp_path / ".runtime/c04-baseline-evidence").glob("*.json"))
