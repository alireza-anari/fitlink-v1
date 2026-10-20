"""Bounded indexed candidates are reauthorized and rendered under sorted anchors."""

from django.contrib.postgres.lookups import TrigramSimilar
from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.db import DatabaseError, connection, models, transaction
from django.db.models import Case, Exists, F, OuterRef, Q, Value, When
from django.db.models.functions import Cast, Floor
from django.utils import timezone

from .contracts import MarketplaceUnavailable, context
from .models import PublicLocation, PublicProfessionalProjection
from .normalization import NORMALIZATION_VERSION, normalize_persian
from .search_contracts import PublicPage, SearchCriteria, decode_cursor, encode_cursor
from .search_index import index_values
from .selectors import public_professionals


class ProjectionRefreshRequired(MarketplaceUnavailable):
    code = "projection_refresh_required"


def candidate_query(criteria, key, at):
    rows = PublicProfessionalProjection.objects.filter(
        state="active",
        normalization_version=NORMALIZATION_VERSION,
    ).filter(Q(next_expiry__isnull=True) | Q(next_expiry__gt=at))
    if criteria.role:
        rows = rows.filter(snapshot__verified_roles__contains=[criteria.role])
    if criteria.country:
        location = PublicLocation.objects.filter(
            projection_id=OuterRef("profile_uuid"),
            country_code=criteria.country,
            normalized_region=criteria.region,
            normalized_city=criteria.city,
        )
        if criteria.mode:
            location = location.filter(modes__contains=[criteria.mode])
        rows = rows.filter(Exists(location))
    elif criteria.mode:
        rows = rows.filter(snapshot__service_modes__contains=[criteria.mode])
    for field in ("specialties", "languages"):
        tokens = getattr(criteria, field)
        if tokens:
            condition = Q()
            for token in tokens:
                condition |= Q(**{f"normalized_filters__{field}__contains": [token]})
            rows = rows.filter(condition)
    if criteria.min_experience is not None:
        rows = rows.filter(experience_years__gte=criteria.min_experience)
    if criteria.max_experience is not None:
        rows = rows.filter(experience_years__lte=criteria.max_experience)
    if criteria.q:
        query = SearchQuery(criteria.q, search_type="plain", config="simple")
        match = Q(search_vector=query)
        if len(criteria.q) >= 3:
            match |= Q(TrigramSimilar(F("normalized_lookup"), Value(criteria.q)))
        rows = rows.filter(match).annotate(
            tier=Case(When(search_vector=query, then=Value(2)), default=Value(1)),
            rank_key=Cast(
                Floor(
                    SearchRank(F("search_vector"), query, cover_density=True) * 1000000
                ),
                models.BigIntegerField(),
            ),
            similarity_key=Cast(
                Floor(TrigramSimilarity("normalized_lookup", criteria.q) * 1000000),
                models.BigIntegerField(),
            ),
        )
    else:
        rows = rows.annotate(tier=Value(0), rank_key=Value(0), similarity_key=Value(0))
    if key is not None:
        tier, rank, similarity, identifier = key
        rows = rows.filter(
            Q(tier__lt=tier)
            | Q(tier=tier, rank_key__lt=rank)
            | Q(tier=tier, rank_key=rank, similarity_key__lt=similarity)
            | Q(
                tier=tier,
                rank_key=rank,
                similarity_key=similarity,
                profile_uuid__gt=identifier,
            )
        )
    return rows.order_by("-tier", "-rank_key", "-similarity_key", "profile_uuid")


def matches_current(criteria, value):
    if criteria.role and criteria.role not in value["verified_roles"]:
        return False
    if criteria.country:
        if not any(
            row["country_code"] == criteria.country
            and normalize_persian(row["region"]) == criteria.region
            and normalize_persian(row["city"]) == criteria.city
            and (not criteria.mode or criteria.mode in row["modes"])
            for row in value.get("locations", [])
        ):
            return False
    elif criteria.mode and criteria.mode not in value.get("service_modes", []):
        return False
    for field in ("specialties", "languages"):
        selected = getattr(criteria, field)
        if selected and not set(selected).intersection(
            normalize_persian(v) for v in value.get(field, [])
        ):
            return False
    years = value.get("experience_years")
    if criteria.min_experience is not None and (
        years is None or years < criteria.min_experience
    ):
        return False
    if criteria.max_experience is not None and (
        years is None or years > criteria.max_experience
    ):
        return False
    return True


def search_public_professionals(
    criteria, cursor, at, *, lock_owners, current_source, request_refresh, release=None
):
    if not isinstance(criteria, SearchCriteria):
        raise ValueError("Invalid search criteria")
    from uuid import UUID

    context(UUID(int=0), at)
    key = decode_cursor(criteria, cursor, at) if cursor is not None else None
    exhausted = False
    try:
        with transaction.atomic():
            with connection.cursor() as database:
                database.execute("SET LOCAL statement_timeout = '2s'")
                database.execute("SET LOCAL lock_timeout = '1s'")
                database.execute("SET LOCAL pg_trgm.similarity_threshold = '0.3'")
            now = max(at, timezone.now())
            candidates = list(
                candidate_query(criteria, key, now).values(
                    "profile_uuid",
                    "tier",
                    "rank_key",
                    "similarity_key",
                    "normalized_name",
                    "normalized_specialties",
                    "normalized_summary",
                    "normalized_biography",
                    "normalized_lookup",
                    "normalized_filters",
                    "experience_years",
                    "normalization_version",
                )[:100]
            )

            def finish(dtos):
                visible = []
                for row, dto in zip(candidates, dtos, strict=True):
                    if dto is None:
                        continue
                    value = dto.as_public_dict()
                    if not matches_current(criteria, value):
                        continue
                    # A changed role summary or damaged index cannot match/rank
                    # on facts absent from the current public release. Catch-up
                    # may suppress discovery; direct current reads remain valid.
                    if criteria.q and any(
                        row[k] != v for k, v in index_values(value).items()
                    ):
                        continue
                    visible.append((row, dto))
                if len(visible) <= criteria.page_size and len(candidates) == 100:
                    return None
                chosen = visible[: criteria.page_size]
                token = None
                if len(visible) > criteria.page_size:
                    last = chosen[-1][0]
                    token = encode_cursor(
                        criteria,
                        (
                            last["tier"],
                            last["rank_key"],
                            last["similarity_key"],
                            last["profile_uuid"],
                        ),
                        max(at, timezone.now()),
                    )
                page = PublicPage(tuple(dto for row, dto in chosen), token)
                return release(page) if release is not None else page

            result = public_professionals(
                tuple(row["profile_uuid"] for row in candidates),
                now,
                lock_owners=lock_owners,
                current_source=current_source,
                release=finish,
            )
            exhausted = result is None
    except DatabaseError:
        raise MarketplaceUnavailable("Marketplace temporarily unavailable") from None
    if exhausted:
        request_refresh(max(at, timezone.now()))
        raise ProjectionRefreshRequired("projection_refresh_required")
    return result
