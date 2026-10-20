"""Projections supply candidates; current server source exclusively authorizes."""

from itertools import islice

from django.db import transaction
from django.utils import timezone

from .contracts import context


def public_professionals(
    identifiers, at, *, lock_owners=None, current_source=None, release=None
):
    identifiers = tuple(islice(identifiers, 101))
    if (
        len(identifiers) > 100
        or len(set(identifiers)) != len(identifiers)
        or not callable(lock_owners)
        or not callable(current_source)
    ):
        raise ValueError("Invalid public read boundary")
    for identifier in identifiers:
        context(identifier, at)
    with transaction.atomic():
        lock_owners(identifiers)
        now = max(at, timezone.now())
        sources = [current_source(identifier, now) for identifier in identifiers]
        dtos = tuple(s.dto() if s is not None else None for s in sources)
        # Serialize/render while owner and source locks still protect authority.
        result = release(dtos) if release is not None else dtos
        for identifier, source in zip(identifiers, sources, strict=True):
            if current_source(identifier, max(at, timezone.now())) != source:
                return None
        return result


def public_professional(
    identifier, at, *, lock_owners=None, current_source=None, release=None
):
    def one(rows):
        if rows[0] is None:
            return None
        return release(rows[0]) if release is not None else rows[0]

    return public_professionals(
        (identifier,),
        at,
        lock_owners=lock_owners,
        current_source=current_source,
        release=one,
    )
