"""The publication contract rejects private facts before any persistence."""

import importlib
import importlib.util
import unittest
from dataclasses import FrozenInstanceError
from uuid import uuid4


def contract():
    name = "apps.professionals.publication_contracts"
    assert importlib.util.find_spec(name) is not None, (
        "Missing explicit professional public-field publication boundary"
    )
    return importlib.import_module(name)


class PublicFieldsTests(unittest.TestCase):
    def test_public_selection_is_frozen_and_rejects_private_fields(self):
        module = contract()
        selection = module.PublicationSelection(
            fields=("display_name", "biography"), roles=("coach",)
        )
        with self.assertRaises(FrozenInstanceError):
            selection.roles = ("nutritionist",)
        for field in (
            "identity_name",
            "phone",
            "birth_date",
            "source_asset",
            "credentials",
            "rating",
            "price",
            "availability",
            "health",
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                module.PublicationSelection(fields=(field,), roles=("coach",))

    def test_media_selection_rejects_identity_and_credential_sources(self):
        module = contract()
        for purpose in ("identity_evidence", "credential_evidence", "athlete"):
            with self.subTest(purpose=purpose), self.assertRaises(ValueError):
                module.PublicationMediaSelection(purpose, uuid4())

    def test_snapshot_rejects_extra_keys_and_unverified_or_fictional_facts(self):
        module = contract()
        valid = {"display_name": "مربی نمونه", "verified_roles": ["coach"]}
        module.validate_public_snapshot(valid)
        for field in ("identity_name", "source_key", "user_uuid", "rating"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                module.validate_public_snapshot({**valid, field: "PRIVATE"})
        for roles in (["both"], ["athlete"], ["coach", "coach"]):
            with self.subTest(roles=roles), self.assertRaises(ValueError):
                module.validate_public_snapshot({**valid, "verified_roles": roles})

    def test_qualification_summary_has_no_private_source_identifiers(self):
        module = contract()
        summary = module.PublicCredentialSummary(
            role="coach",
            title="مدرک نمونه",
            issuer="مرجع نمونه",
            type_label="گواهی مربیگری",
            issued_on=None,
            expires_on=None,
        )
        self.assertEqual(
            set(summary.as_public_dict()),
            {"role", "title", "issuer", "type_label", "issued_on", "expires_on"},
        )
        with self.assertRaises(ValueError):
            module.PublicCredentialSummary(
                role="identity",
                title="PRIVATE",
                issuer="PRIVATE",
                type_label="PRIVATE",
                issued_on=None,
                expires_on=None,
            )


if __name__ == "__main__":
    unittest.main()
