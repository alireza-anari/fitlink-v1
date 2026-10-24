"""Diagnostic-only named test of the unchanged populated upgrade verifier."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from docker import c03_upgrade_probe as probe


class PopulatedPreservation(unittest.TestCase):
    def test_task7_populated_upgrade_accepts_exact_moderation_metadata(self):
        try:
            probe._impl.main()
        except AssertionError as error:
            print(
                "C03_TASK14 preservation_" + probe.preservation_predicate(error),
                flush=True,
            )
            raise
        print("C03_TASK14 preservation_verified", flush=True)


if __name__ == "__main__":
    if sys.argv[1:] != ["/rehearsal/metadata.json"]:
        raise SystemExit(2)
    sys.argv = ["docker/c03_upgrade_probe.py", "verify", "/rehearsal/metadata.json"]
    result = unittest.TextTestRunner().run(
        unittest.defaultTestLoader.loadTestsFromTestCase(PopulatedPreservation)
    )
    raise SystemExit(0 if result.wasSuccessful() else 1)
