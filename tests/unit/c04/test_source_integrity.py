"""Mutation controls prove the approved C03 source tree stays immutable."""

import importlib
import shutil
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]


def test_original_c03_fixture_tree_mismatch_rejected(tmp_path):
    spec = importlib.util.find_spec("docker.c04_baseline")
    assert spec is not None, "Missing immutable C03 source verifier"
    module = importlib.import_module("docker.c04_baseline")
    source = ROOT / ".runtime/c03"
    assert module.verify_baseline(source) == module.C03_TREE
    copy = tmp_path / "c03"
    shutil.copytree(
        source,
        copy,
        ignore=shutil.ignore_patterns(
            ".git", ".venv", ".runtime", "node_modules", "__pycache__"
        ),
    )
    assert module.verify_baseline(copy) == module.C03_TREE
    path = copy / "apps/professionals/selectors.py"
    path.write_bytes(path.read_bytes() + b"\n# deliberate mutation\n")
    with pytest.raises(ValueError, match="baseline"):
        module.verify_baseline(copy)
