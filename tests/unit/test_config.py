import pytest

from tremor_api.config import StewardSettings


def test_steward_url_defaults_to_in_namespace_service(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STEWARD_URL", raising=False)

    assert StewardSettings().url == "http://steward-api:8000"


def test_steward_url_comes_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEWARD_URL", "http://steward-api.preview-demo:8000")

    assert StewardSettings().url == "http://steward-api.preview-demo:8000"


def test_steward_timeout_is_two_seconds() -> None:
    assert StewardSettings().timeout_seconds == 2.0
