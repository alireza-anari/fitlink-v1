import importlib
import os
import subprocess
import sys

import pytest

pytestmark = pytest.mark.unit


def boot(module, values):
    env = {k: v for k, v in os.environ.items() if k in ("PATH", "SYSTEMROOT")}
    env.update(values)
    return subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import importlib,sys\ntry: importlib.import_module(sys.argv[1])\n"
                "except Exception as e:\n print(type(e).__name__+': '+str(e),"
                "file=sys.stderr);sys.exit(1)"
            ),
            module,
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_missing_production_secret_fails():
    result = boot("config.settings.production", {})
    assert result.returncode != 0
    assert "ImproperlyConfigured" in result.stderr
    assert "DJANGO_SECRET_KEY" in result.stderr


def test_blank_required_value_fails_without_value_leak(monkeypatch):
    env = importlib.import_module("config.settings.env")
    monkeypatch.setenv("SAMPLE_SECRET", "   ")
    with pytest.raises(Exception, match="SAMPLE_SECRET"):
        env.str_value("SAMPLE_SECRET", required=True)


def test_invalid_bool_fails(monkeypatch):
    env = importlib.import_module("config.settings.env")
    monkeypatch.setenv("SAMPLE_BOOL", "secret-text")
    with pytest.raises(Exception, match="SAMPLE_BOOL") as error:
        env.bool_value("SAMPLE_BOOL")
    assert "secret-text" not in str(error.value)


@pytest.mark.parametrize(
    "value,expected", [("TRUE", True), ("0", False), ("false", False), ("1", True)]
)
def test_bool_contract(monkeypatch, value, expected):
    env = importlib.import_module("config.settings.env")
    monkeypatch.setenv("BOOL", value)
    assert env.bool_value("BOOL") is expected


def test_int_and_csv(monkeypatch):
    env = importlib.import_module("config.settings.env")
    monkeypatch.setenv("COUNT", "2")
    assert env.int_value("COUNT", minimum=1) == 2
    monkeypatch.setenv("COUNT", "0")
    with pytest.raises(Exception, match="COUNT"):
        env.int_value("COUNT", minimum=1)
    monkeypatch.setenv("HOSTS", "a,b")
    assert env.csv_value("HOSTS") == ("a", "b")
