import pytest
from django.test import Client

pytestmark = pytest.mark.unit


def test_neutral_rtl_page():
    response = Client().get("/")
    assert response.status_code == 200
    html = response.content.decode()
    for item in [
        'lang="fa"',
        'dir="rtl"',
        'name="viewport"',
        "زیرساخت فیت‌لینک آماده است",
        'type="module"',
        "dist/app.css",
        "src/app.js",
    ]:
        assert item in html
    assert "<form" not in html and "login" not in html


def test_manifest_template_paths(tmp_path):
    from django.test import override_settings
    from django.core.management import call_command
    import json

    with override_settings(STATIC_ROOT=tmp_path, STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
    }):
        call_command("collectstatic", interactive=False, verbosity=0, ignore=["src/styles.css"])
        manifest = json.loads((tmp_path / "staticfiles.json").read_text())
        assert "src/styles.css" not in manifest["paths"]
        for path in ("dist/app.css", "src/app.js"):
            hashed = manifest["paths"][path]
            assert hashed != path
            assert (tmp_path / hashed).stat().st_size > 0
            assert hashed in Client().get("/").content.decode()
