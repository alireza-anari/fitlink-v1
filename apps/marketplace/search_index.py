"""Only allowlisted immutable release facts contribute searchable tokens."""

from django.contrib.postgres.search import SearchVector

from .normalization import NORMALIZATION_VERSION, normalize_persian


def index_values(snapshot):
    name = normalize_persian(snapshot.get("display_name", ""))
    specialties = [normalize_persian(v) for v in snapshot.get("specialties", [])]
    summary = " ".join(
        row["title"] for row in snapshot.get("qualification_summaries", [])
    )
    locations = " ".join(
        row["region"] + " " + row["city"] for row in snapshot.get("locations", [])
    )
    return dict(
        normalized_name=name,
        normalized_specialties=" ".join(specialties),
        normalized_summary=normalize_persian(summary + " " + locations),
        normalized_biography=normalize_persian(snapshot.get("biography", "")),
        normalized_lookup=" ".join([name, *specialties]),
        normalized_filters=dict(
            specialties=specialties,
            languages=[normalize_persian(v) for v in snapshot.get("languages", [])],
        ),
        experience_years=snapshot.get("experience_years"),
        normalization_version=NORMALIZATION_VERSION,
    )


def search_vector():
    return (
        SearchVector(
            "normalized_name", "normalized_specialties", config="simple", weight="A"
        )
        + SearchVector("normalized_summary", config="simple", weight="B")
        + SearchVector("normalized_biography", config="simple", weight="C")
    )
