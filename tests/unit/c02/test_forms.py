import importlib

import pytest

pytestmark = pytest.mark.unit


def forms():
    return importlib.import_module("apps.accounts.forms")


@pytest.mark.parametrize(
    "calendar,birth_date", [("gregorian", "1990-01-01"), ("jalali", "۱۳۶۸-۱۰-۱۱")]
)
def test_entry_accepts_labeled_date_and_persian_phone(calendar, birth_date):
    form = forms().EntryForm(
        data={
            "phone": "۰۹۱۲۳۴۵۶۷۸۹",
            "birth_date": birth_date,
            "calendar": calendar,
            "adult_attested": True,
            "entry_hint": "athlete",
        }
    )
    assert form.is_valid(), form.errors
    assert form.cleaned_data["phone"] == "+989123456789"
    assert form.cleaned_data["birth_date"].isoformat() == "1990-01-01"


@pytest.mark.parametrize(
    "change",
    [
        {"birth_date": "2020-01-01"},
        {"adult_attested": False},
        {"calendar": ""},
        {"calendar": "invented"},
        {"birth_date": "invalid"},
        {"entry_hint": "staff"},
        {"phone": "invalid"},
    ],
)
def test_entry_denies_minor_unlabeled_or_unattested_data(change):
    data = {
        "phone": "09123456789",
        "birth_date": "1990-01-01",
        "calendar": "gregorian",
        "adult_attested": True,
        "entry_hint": "athlete",
        **change,
    }
    assert not forms().EntryForm(data=data).is_valid()


def test_privacy_confirmation_is_explicit_and_default_denied():
    assert not forms().PrivacyForm(data={"kind": "delete"}).is_valid()
    assert forms().PrivacyForm(data={"kind": "delete", "confirmed": True}).is_valid()


def test_persian_code_normalization_and_masked_fields_are_not_credentials():
    form = forms().VerifyForm(data={"code": "۱۲۳۴۵۶"})
    assert form.is_valid()
    assert form.cleaned_data["code"] == "123456"
    assert 'type="password"' not in form.as_p()
    assert form.fields["code"].widget.attrs["autocomplete"] == "one-time-code"


@pytest.mark.parametrize(
    "data",
    [
        {"locale": "xx", "timezone": "UTC"},
        {"locale": "fa", "timezone": "invented/zone"},
    ],
)
def test_preferences_reject_unknown_values(data):
    assert not forms().PreferencesForm(data=data).is_valid()


def test_proof_error_renders_without_echoing_code_or_crashing():
    from apps.accounts.otp import OtpThrottled
    from apps.accounts.views import clear_proof_error

    form = clear_proof_error(OtpThrottled(60))
    assert form.errors
    assert "لطفاً" in str(form.non_field_errors())
    assert form["code"].value() in (None, "")


@pytest.mark.parametrize("version", [None, "", "0", "-1", "1.5", str(2**63)])
def test_staff_rejects_missing_or_unbounded_case_version(version):
    assert not forms().StaffVersionForm(data={"expected_version": version}).is_valid()


def test_staff_accepts_positive_case_version():
    form = forms().StaffVersionForm(data={"expected_version": "3"})
    assert form.is_valid()
    assert form.cleaned_data["expected_version"] == 3
