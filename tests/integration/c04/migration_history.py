"""Historical schema probes own a fresh PostgreSQL database, never parent data."""

from contextlib import contextmanager
from uuid import uuid4

from django.db import connections
from psycopg import sql

C02_TARGETS = (
    ("accounts", "0013_invitereferrallink_referralattribution_and_more"),
    ("auth", "0012_alter_user_first_name_max_length"),
    ("contenttypes", "0002_remove_content_type_name"),
    ("governance", "0010_outboxdeliveryreceipt"),
    ("sessions", "0001_initial"),
)
POST_C02 = frozenset({"assets", "athletes", "professionals", "marketplace"})


def historical_c02_targets():
    return list(C02_TARGETS)


def historical_unapply_targets(latest):
    labels = {label for label, _ in latest}
    if labels - {label for label, _ in C02_TARGETS} - POST_C02:
        raise ValueError("Unexpected migration domain")
    return [(label, None) for label in sorted(labels & POST_C02)]


@contextmanager
def isolated_history_database(parent):
    if (
        parent.vendor != "postgresql"
        or parent.in_atomic_block
        or not parent.get_autocommit()
    ):
        raise RuntimeError("Historical probe requires autocommit PostgreSQL")
    identifier = uuid4().hex
    name = "test_c04_history_" + identifier
    alias = "c04_history_" + identifier
    if name == parent.settings_dict["NAME"] or alias in connections:
        raise RuntimeError("Historical probe collision")
    probe = parent.copy(alias=alias)
    probe.settings_dict["NAME"] = name
    probe.settings_dict["CONN_MAX_AGE"] = 0
    created = registered = False
    try:
        with parent.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE DATABASE {} TEMPLATE template0").format(
                    sql.Identifier(name)
                )
            )
        created = True
        # A dynamically created test connection; configured parent aliases and
        # their database names are never rewritten or migrated backwards.
        connections[alias] = probe
        registered = True
        yield probe
    finally:
        probe.close()
        if registered:
            del connections[alias]
        if created:
            with parent.cursor() as cursor:
                cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(name)))
