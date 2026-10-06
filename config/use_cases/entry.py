"""Entry choices are acquisition hints; no role or profile is created."""

from apps.governance.flags import professional_entry_enabled


def professional_entry_available() -> bool:
    return professional_entry_enabled()
