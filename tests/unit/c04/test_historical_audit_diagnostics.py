"""A failed historical HTTP read remains fatal and reports only finite metadata."""

from unittest.mock import patch
from urllib.error import HTTPError

import pytest

from docker import c03_asset_restart_probe as probe


@pytest.mark.parametrize("status", [403, 404, 410, 429, 502, 503])
def test_historical_http_failure_has_status_without_url_headers_or_body(status):
    error = HTTPError(
        "https://synthetic.invalid/private-query",
        status,
        "private-body",
        {"Authorization": "private-header"},
        None,
    )
    with (
        patch.dict("os.environ", {"GITHUB_TOKEN": "synthetic-private-token"}),
        patch("urllib.request.build_opener") as factory,
        patch.object(probe, "evidence") as report,
    ):
        factory.return_value.open.side_effect = error
        with pytest.raises(HTTPError) as observed:
            probe.audit()
        assert observed.value is error
        report.assert_called_once_with(
            "historical_http_error", http_status=status, endpoint_family="actions"
        )
        assert factory.return_value.open.call_count == 1
