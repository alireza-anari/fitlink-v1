import pytest
from django.utils import timezone


@pytest.mark.parametrize("limit", [0, 26, True, "25", None])
def test_queue_rejects_unbounded_page_before_authority_or_database(limit):
    from apps.governance import moderation

    command = getattr(moderation, "moderation_queue", None)
    assert callable(command), "Missing bounded capability moderation queue"
    with pytest.raises(ValueError):
        command(None, None, "security_review", timezone.now(), limit=limit)
