import importlib

import pytest


def test_verification_and_application_contracts_exist():
    otp = importlib.import_module("apps.accounts.otp")
    assert callable(getattr(otp, "verify_otp", None)), (
        "missing atomic proof consumption"
    )
    assert callable(getattr(otp, "apply_verified_proof", None)), (
        "missing one-time proof application"
    )


def test_code_input_only_bounded_supported_digits():
    otp = importlib.import_module("apps.accounts.otp")
    assert callable(getattr(otp, "normalize_code", None)), "missing bounded OTP input"
    assert otp.normalize_code("۰۰۱۲۳۴") == "001234"
    assert otp.normalize_code("٠٠١٢٣٤") == "001234"
    for value in ["12345", "1234567", " 123456", "１２３４５６", "12345\u202e", None]:
        with pytest.raises(ValueError):
            otp.normalize_code(value)
