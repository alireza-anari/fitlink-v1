"""Closed internal inert role boundary pending real PostgreSQL RED."""


def define_assistant_role(actor, assistant_uuid, operation_id, at, **hooks):
    raise PermissionError("Assistant definition unavailable")


def revoke_assistant_role(
    actor, membership_uuid, expected_version, operation_id, at, **hooks
):
    raise PermissionError("Assistant definition unavailable")
