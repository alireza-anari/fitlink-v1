"""One bounded real-service recovery probe; never an acceptance manifest."""

import cProfile
import json
import math
import os
import pstats
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYMBOLS = {
    ("tests/integration/c04/search_helpers.py", "create"): "corpus",
    (
        "tests/integration/c04/search_helpers.py",
        "coach_approved",
    ): "single_role_approval",
    ("tests/integration/c03/test_verification_decisions.py", "approved"): "approval",
    ("tests/integration/c04/publication_helpers.py", "prepare"): "publication_prepare",
    ("tests/integration/c04/publication_helpers.py", "confirm"): "publication_confirm",
    ("config/use_cases/publication.py", "unpublish_profile"): "withdrawal",
    ("config/use_cases/marketplace.py", "reconcile_publications"): "reconciliation",
    ("apps/marketplace/search.py", "search_public_professionals"): "search",
}
SELECTION = [
    "tests/integration/c04/test_search_eligibility.py::"
    "test_candidate_budget_fails_without_partial_output_and_recovers",
    "tests/integration/c04/test_search_query_plans.py::"
    "test_real_bounded_fts_trigram_query_plan",
]


def summarize(stats):
    rows = []
    for (filename, _line, function), values in stats.items():
        label = SYMBOLS.get((filename, function))
        if label is None:
            try:
                relative = Path(filename).relative_to(ROOT).as_posix()
            except ValueError:
                continue
            label = SYMBOLS.get((relative, function))
        if label is None:
            continue
        primitive, calls, own, cumulative, _callers = values
        if not (
            type(primitive) is int
            and type(calls) is int
            and 0 <= primitive <= calls <= 100000000
            and all(math.isfinite(n) and 0 <= n <= 3600 for n in (own, cumulative))
        ):
            raise ValueError("Profile counters denied")
        rows.append(
            {
                "symbol": label,
                "primitive_calls": primitive,
                "calls": calls,
                "self_seconds": round(own, 3),
                "cumulative_seconds": round(cumulative, 3),
            }
        )
    return sorted(rows, key=lambda row: row["symbol"])


def main():
    import pytest
    from django.db.backends.utils import CursorWrapper

    sys.path.insert(0, str(ROOT))
    SYMBOLS[
        (str(Path(CursorWrapper.execute.__code__.co_filename).resolve()), "execute")
    ] = "database_execute"
    # The absolute installed path is used only as a lookup key, never exported.
    profiler = cProfile.Profile()
    code = profiler.runcall(
        pytest.main,
        [*SELECTION, "-q", "--strict-markers", "--tb=no", "--show-capture=no"],
    )
    report = {
        "acceptance": False,
        "head_sha": os.environ["GITHUB_SHA"],
        "pytest_exit": int(code),
        "functions": summarize(pstats.Stats(profiler).stats),
    }
    folder = ROOT / ".runtime/c04-recovery-profile"
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    (folder / "timing.json").write_text(json.dumps(report, sort_keys=True) + "\n")
    print("C04_RECOVERY_PROFILE " + json.dumps(report, sort_keys=True), flush=True)
    return int(code)


if __name__ == "__main__":
    raise SystemExit(main())
