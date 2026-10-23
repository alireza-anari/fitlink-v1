"""Recovery profiling exports fixed symbols and numeric counters only."""

import importlib.util
import json
import unittest
from pathlib import Path


class RecoveryProfileTests(unittest.TestCase):
    def test_profile_summary_excludes_paths_callers_and_unknown_symbols(self):
        path = Path("docker/c04_recovery_profile.py")
        assert path.exists(), "Missing bounded Task6 recovery profiler"
        spec = importlib.util.spec_from_file_location("profile_reader", path)
        reader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reader)
        known = (
            str(Path("tests/integration/c04/search_helpers.py").resolve()),
            40,
            "create",
        )
        secret = ("/PRIVATE_PATH/secret.py", 1, "PRIVATE_NAME")
        result = reader.summarize(
            {known: (2, 3, 1.2, 4.5, {secret: (1,)}), secret: (1, 1, 9.0, 9.0, {})}
        )
        assert result == [
            {
                "symbol": "corpus",
                "primitive_calls": 2,
                "calls": 3,
                "self_seconds": 1.2,
                "cumulative_seconds": 4.5,
            }
        ]
        assert "PRIVATE" not in json.dumps(result)


if __name__ == "__main__":
    unittest.main()
