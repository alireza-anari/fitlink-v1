"""Fail a C04 pytest command on required skips or expected failures."""

import pytest


class RequiredEvidence:
    def pytest_sessionfinish(self, session):
        terminal = session.config.pluginmanager.get_plugin("terminalreporter")
        if terminal and any(
            terminal.stats.get(k) for k in ("skipped", "xfailed", "xpassed")
        ):
            session.exitstatus = 1


if __name__ == "__main__":
    import sys

    raise SystemExit(pytest.main(sys.argv[1:], plugins=[RequiredEvidence()]))
