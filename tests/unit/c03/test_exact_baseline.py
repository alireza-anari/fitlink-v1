"""Exact C02 source integrity, independent of current C03 source."""

import json
import shutil
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]
C02_TREE = "ed788191bb6f5011e6b35a63823ae8183af7b53d"


def _clone_exact_c02(source, target):
    return shutil.copytree(
        source,
        target,
        symlinks=True,
        ignore=shutil.ignore_patterns(".git"),
    )


@pytest.mark.parametrize("defect", ["modified", "missing", "extra", "symlink"])
def test_exact_c02_source_tamper_missing_extra_symlink(tmp_path, defect):
    from docker.c03_baseline import verify_baseline

    source = ROOT / ".runtime/c02"
    # This assertion must pass before a deliberate source mutation can count RED.
    assert verify_baseline(source) == C02_TREE
    target = tmp_path / "baseline"
    _clone_exact_c02(source, target)
    assert verify_baseline(target) == C02_TREE
    path = target / "apps/accounts/models.py"
    if defect == "modified":
        path.write_bytes(path.read_bytes() + b"\n# deliberate source change\n")
    elif defect == "extra":
        path.with_name("unexpected.py").write_text("# unexpected source\n")
    else:
        path.unlink()
        if defect == "symlink":
            path.symlink_to(source / "apps/accounts/models.py")
    with pytest.raises(ValueError, match="baseline"):
        verify_baseline(target)


def test_exact_c02_manifest_and_source_identity():
    from docker.c03_baseline import verify_baseline

    assert verify_baseline(ROOT / ".runtime/c02") == C02_TREE


def test_exact_ref_verification_without_git_binary(tmp_path, monkeypatch):
    from docker import c03_baseline

    target = tmp_path / "baseline"
    _clone_exact_c02(ROOT / ".runtime/c02", target)
    metadata = target / ".git"
    metadata.mkdir()
    (metadata / "HEAD").write_text(c03_baseline.C02_COMMIT + "\n")

    def unavailable(*args, **kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(c03_baseline.subprocess, "check_output", unavailable)
    assert c03_baseline.verify_baseline(target) == C02_TREE
    (metadata / "HEAD").write_text("a" * 40 + "\n")
    with pytest.raises(ValueError, match="baseline"):
        c03_baseline.verify_baseline(target)


def test_exact_c02_wrong_checkout_ref_rejected(tmp_path):
    from docker.c03_baseline import verify_baseline

    target = tmp_path / "baseline"
    _clone_exact_c02(ROOT / ".runtime/c02", target)
    assert verify_baseline(target) == C02_TREE
    (target / ".git").write_text("gitdir: " + str(ROOT / ".git") + "\n")
    with pytest.raises(ValueError, match="baseline"):
        verify_baseline(target)


@pytest.mark.parametrize(
    "defect", ["mode", "parent_symlink", "cache_source", "extra_build_output"]
)
def test_exact_c02_source_modes_and_generated_namespace_bounds(tmp_path, defect):
    from docker.c03_baseline import verify_baseline

    target = tmp_path / "baseline"
    _clone_exact_c02(ROOT / ".runtime/c02", target)
    assert verify_baseline(target) == C02_TREE
    path = target / "apps/accounts/models.py"
    if defect == "mode":
        path.chmod(0o755)
    elif defect == "parent_symlink":
        directory = target / "apps/accounts"
        directory.rename(target / "saved")
        directory.symlink_to(target / "saved", target_is_directory=True)
    elif defect == "cache_source":
        path = target / "apps/accounts/__pycache__/injected.py"
        path.parent.mkdir(exist_ok=True)
        path.write_text("# unexpected source in generated namespace\n")
    else:
        path = target / "static/dist/unexpected.css"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("/* unenumerated build output */\n")
    with pytest.raises(ValueError, match="baseline"):
        verify_baseline(target)


@pytest.mark.parametrize("field", ["commit", "tree", "blob"])
def test_exact_c02_wrong_manifest_identity_rejected(monkeypatch, field):
    from docker import c03_baseline

    manifest = json.loads((ROOT / "docker/c03_source_manifest.json").read_text())
    if field == "blob":
        next(e for e in manifest["entries"] if e["type"] == "blob")["sha"] = "a" * 40
    else:
        manifest[field] = "a" * 40
    monkeypatch.setattr(c03_baseline.json, "loads", lambda _: manifest)
    with pytest.raises(ValueError, match="baseline"):
        c03_baseline.verify_baseline(ROOT / ".runtime/c02")
