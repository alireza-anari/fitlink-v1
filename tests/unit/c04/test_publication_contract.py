"""Bounded publication facts never substitute declarations for verified roles."""

import unittest
from datetime import UTC, datetime
from uuid import uuid4

from tests.unit.c04.test_public_fields import contract


class PublicationContractTests(unittest.TestCase):
    def test_default_slug_uses_only_public_profile_uuid(self):
        module = contract()
        identifier = uuid4()
        self.assertEqual(module.canonical_slug(identifier, None), "p-" + identifier.hex)
        for slug in (
            "admin",
            "api",
            "search",
            "media",
            "../private",
            "PRIVATE",
            "x" * 81,
        ):
            with self.subTest(slug=slug), self.assertRaises(ValueError):
                module.canonical_slug(identifier, slug)

    def test_mutable_duplicate_and_undeclared_selection_shapes_rejected(self):
        module = contract()
        for fields, roles in (
            (["display_name"], ("coach",)),
            (("display_name", "display_name"), ("coach",)),
            (("display_name",), ()),
            (("display_name",), ("both",)),
        ):
            with (
                self.subTest(fields=fields, roles=roles),
                self.assertRaises(ValueError),
            ):
                module.PublicationSelection(fields=fields, roles=roles)
        with self.assertRaises(ValueError):
            module.PublicationSelection(
                fields=("display_name",),
                roles=("coach",),
                valid_until=datetime(2027, 1, 1),
            )
        module.PublicationSelection(
            fields=("display_name",),
            roles=("coach",),
            valid_until=datetime(2027, 1, 1, tzinfo=UTC),
        )

    def test_summary_cannot_publish_an_unselected_role_or_private_link(self):
        module = contract()
        snapshot = {
            "display_name": "Synthetic",
            "verified_roles": ["coach"],
            "qualification_summaries": [
                {
                    "role": "nutritionist",
                    "title": "Synthetic",
                    "issuer": "Synthetic",
                    "type_label": "Synthetic",
                    "issued_on": None,
                    "expires_on": None,
                }
            ],
        }
        with self.assertRaises(ValueError):
            module.validate_public_snapshot(snapshot)
        snapshot["qualification_summaries"][0]["role"] = "coach"
        module.validate_public_snapshot(snapshot)
        snapshot["qualification_summaries"][0]["source_url"] = "PRIVATE"
        with self.assertRaises(ValueError):
            module.validate_public_snapshot(snapshot)

    def test_truthful_unknown_experience_and_broad_location_only(self):
        module = contract()
        snapshot = {
            "display_name": "Synthetic",
            "verified_roles": ["coach"],
            "experience_years": None,
            "locations": [
                {
                    "country_code": "IR",
                    "region": "نمونه",
                    "city": "نمونه",
                    "modes": ["in_person"],
                }
            ],
        }
        module.validate_public_snapshot(snapshot)
        snapshot["experience_years"] = True
        with self.assertRaises(ValueError):
            module.validate_public_snapshot(snapshot)
        snapshot["experience_years"] = None
        snapshot["locations"][0]["address"] = "PRIVATE"
        with self.assertRaises(ValueError):
            module.validate_public_snapshot(snapshot)

    def test_snapshot_text_and_total_payload_are_bounded(self):
        module = contract()
        snapshot = {"display_name": "Synthetic", "verified_roles": ["coach"]}
        for biography in ("x" * 2001, "<script>PRIVATE</script>", "PRIVATE\x00"):
            with self.subTest(length=len(biography)), self.assertRaises(ValueError):
                module.validate_public_snapshot({**snapshot, "biography": biography})


if __name__ == "__main__":
    unittest.main()
