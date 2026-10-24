from uuid import uuid4

import pytest
from django.utils import timezone


@pytest.mark.parametrize("bad", ["case", "copy", "step"])
def test_invalid_case_media_binding_is_denied_before_database_or_storage(bad):
    from config.use_cases import public_content

    command = getattr(public_content, "read_public_moderation_media", None)
    assert callable(command), "Missing assigned exact-revision media reader"
    values = {"case": uuid4(), "copy": uuid4(), "step": uuid4()}
    values[bad] = "invalid"
    with pytest.raises(ValueError):
        command(
            None,
            values["case"],
            values["copy"],
            values["step"],
            "staff_assigned",
            timezone.now(),
        )
