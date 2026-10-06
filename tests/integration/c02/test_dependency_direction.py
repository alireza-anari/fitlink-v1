import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def test_account_domain_does_not_import_governance_or_composition():
    # Transport adapters are composed at the root; domain modules cannot invert it.
    for path in Path("apps/accounts").glob("*.py"):
        if path.name in {"api.py", "views.py", "staff_views.py", "urls.py"}:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            modules = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or ""]
            assert not any(
                m.startswith(("apps.governance", "config.use_cases")) for m in modules
            ), path
