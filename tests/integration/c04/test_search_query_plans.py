"""Real PostgreSQL planner on 30k synthetic released-text index documents.

The temporary relation shadows only the candidate index for EXPLAIN. It never
replaces source authorization or supplies a public response. Actual corpus and
current-authority behavior are separately tested through real domain services.
"""

import json

import pytest
from django.db import connection, transaction
from django.utils import timezone

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def walk(node):
    yield node
    for child in node.get("Plans", []):
        yield from walk(child)


def test_real_bounded_fts_trigram_query_plan(corpus, record_property):
    from apps.marketplace.contracts import SearchCriteria
    from apps.marketplace.search import candidate_query

    corpus()
    with transaction.atomic():
        with connection.cursor() as database:
            database.execute(
                "CREATE TEMP TABLE marketplace_publicprofessionalprojection "
                "(LIKE public.marketplace_publicprofessionalprojection "
                "INCLUDING DEFAULTS INCLUDING CONSTRAINTS INCLUDING INDEXES) "
                "ON COMMIT DROP"
            )
            database.execute("""
                INSERT INTO marketplace_publicprofessionalprojection
                SELECT (jsonb_populate_record(
                    NULL::marketplace_publicprofessionalprojection,
                    to_jsonb(p) || jsonb_build_object(
                        'profile_uuid',md5('c04-plan-document-' || n::text),
                        'normalized_name',CASE WHEN n<=10 THEN 'زمردیاب'
                            ELSE 'مربی ورزش ' || n::text END,
                        'normalized_lookup',CASE WHEN n<=10 THEN 'زمردیاب'
                            ELSE 'مربی ورزش ' || n::text END,
                        'normalized_specialties','',
                        'normalized_summary','',
                        'normalized_biography','',
                        'search_vector',to_tsvector('simple',
                            CASE WHEN n<=10 THEN 'زمردیاب'
                            ELSE 'مربی ورزش ' || n::text END)::text
                    )
                )).* FROM public.marketplace_publicprofessionalprojection p
                CROSS JOIN generate_series(1,30000) n
            """)
            database.execute(
                "SELECT count(*) FROM marketplace_publicprofessionalprojection"
            )
            cardinality = database.fetchone()[0]
            assert cardinality == 30000
            database.execute("ANALYZE marketplace_publicprofessionalprojection")
            database.execute("SET LOCAL statement_timeout='2s'")
            database.execute("SET LOCAL pg_trgm.similarity_threshold='0.3'")
        query = candidate_query(SearchCriteria(q="زمردیاب"), None, timezone.now())[:100]
        plan = json.loads(query.explain(analyze=True, buffers=True, format="json"))[0]
        nodes = list(walk(plan["Plan"]))
        indexes = [node for node in nodes if "Index" in node.get("Node Type", "")]
        conditions = " ".join(node.get("Index Cond", "") for node in indexes)
        assert "search_vector" in conditions and "normalized_lookup" in conditions
        assert len(indexes) >= 2
        assert plan["Plan"]["Actual Rows"] == 10
        assert plan["Execution Time"] < 2000
        blocks = sum(
            plan["Plan"].get(key, 0)
            for key in (
                "Shared Hit Blocks",
                "Shared Read Blocks",
                "Local Hit Blocks",
                "Local Read Blocks",
            )
        )
        assert blocks <= 2000
        record_property(
            "c04_query_plan",
            {
                "rows": cardinality,
                "returned": plan["Plan"]["Actual Rows"],
                "index_nodes": len(indexes),
                "planning_ms": plan["Planning Time"],
                "execution_ms": plan["Execution Time"],
                "buffer_blocks": blocks,
            },
        )
