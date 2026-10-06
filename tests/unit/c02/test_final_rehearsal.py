import shutil
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]


def test_immutable_c01_fixture_has_exact_source_tree():
    from docker.c02_baseline import verify_baseline

    assert (
        verify_baseline(ROOT / ".runtime/c01")
        == "4dff1ebd5a32ed0359552bf29012d9d1ecf09b24"
    )


@pytest.mark.parametrize("defect", ["modified", "missing", "symlink", "unexpected"])
def test_baseline_verification_rejects_untrusted_source(tmp_path, defect):
    from docker.c02_baseline import verify_baseline

    source = ROOT / ".runtime/c01"
    shutil.copytree(
        source,
        tmp_path / "baseline",
        ignore=shutil.ignore_patterns(
            ".env.verify",
            ".ruff_cache",
            ".mypy_cache",
            ".git",
            ".venv",
            "node_modules",
            "__pycache__",
            "staticfiles",
            ".pytest_cache",
        ),
    )
    path = tmp_path / "baseline/apps/accounts/models.py"
    if defect == "unexpected":
        path.with_name("injected.py").write_text("raise RuntimeError('unexpected')\n")
    elif defect == "modified":
        path.write_text(path.read_text() + "\n# changed\n")
    else:
        path.unlink()
        if defect == "symlink":
            path.symlink_to(source / "apps/accounts/models.py")
    with pytest.raises(ValueError, match="baseline"):
        verify_baseline(tmp_path / "baseline")


def test_baseline_copy_never_reads_generated_environment(monkeypatch, tmp_path):
    original = shutil.copytree

    def guarded_copy(source, destination, *args, **kwargs):
        # Compose creates this protected runtime file; it is not C01 source.
        if Path(source) == ROOT / ".runtime/c01":
            assert ".env.verify" in kwargs["ignore"](str(source), [".env.verify"])
        return original(source, destination, *args, **kwargs)

    monkeypatch.setattr(shutil, "copytree", guarded_copy)
    test_baseline_verification_rejects_untrusted_source(tmp_path, "modified")
