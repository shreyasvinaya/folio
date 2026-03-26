from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "bin" / "update_scholar_citations.py"
)


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "update_scholar_citations", MODULE_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class _FakeNow:
    def __init__(self, today: str) -> None:
        self.today = today

    def strftime(self, _: str) -> str:
        return self.today


class _FakeDateTime:
    def __init__(self, today: str) -> None:
        self.today = today

    def now(self) -> _FakeNow:
        return _FakeNow(self.today)


def set_today(
    monkeypatch: pytest.MonkeyPatch, module, today: str = "2026-03-27"
) -> None:
    monkeypatch.setattr(module, "datetime", _FakeDateTime(today))


def test_skips_fetch_when_already_updated_today(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = load_module()
    today = "2026-03-27"
    citation_path = tmp_path / "citations.yml"
    citation_path.write_text(
        yaml.safe_dump({"metadata": {"last_updated": today}, "papers": {"p1": {}}})
    )

    monkeypatch.setattr(module, "OUTPUT_FILE", citation_path)
    monkeypatch.setattr(module, "load_scholar_user_id", lambda: "abc123")
    set_today(monkeypatch, module, today)

    fetch_called = False

    def fail_fetch(_: str) -> dict[str, object]:
        nonlocal fetch_called
        fetch_called = True
        raise AssertionError("fetch_author_data should not be called")

    monkeypatch.setattr(module, "fetch_author_data", fail_fetch)

    module.get_scholar_citations()

    assert fetch_called is False


def test_keeps_existing_file_on_fetch_timeout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = load_module()
    citation_path = tmp_path / "citations.yml"
    original_payload = {
        "metadata": {"last_updated": "2026-03-20"},
        "papers": {"paper-1": {"title": "Existing", "year": "2024", "citations": 3}},
    }
    citation_path.write_text(yaml.safe_dump(original_payload))

    monkeypatch.setattr(module, "OUTPUT_FILE", citation_path)
    monkeypatch.setattr(module, "ALLOW_STALE_ON_FETCH_FAILURE", True)
    monkeypatch.setattr(module, "load_scholar_user_id", lambda: "abc123")
    set_today(monkeypatch, module)
    monkeypatch.setattr(
        module,
        "fetch_author_data",
        lambda _: (_ for _ in ()).throw(module.ScholarFetchTimeoutError("timeout")),
    )

    module.get_scholar_citations()

    assert yaml.safe_load(citation_path.read_text()) == original_payload


def test_raises_when_fetch_fails_without_existing_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = load_module()
    monkeypatch.setattr(module, "OUTPUT_FILE", tmp_path / "missing.yml")
    monkeypatch.setattr(module, "ALLOW_STALE_ON_FETCH_FAILURE", True)
    monkeypatch.setattr(module, "load_scholar_user_id", lambda: "abc123")
    set_today(monkeypatch, module)
    monkeypatch.setattr(
        module,
        "fetch_author_data",
        lambda _: (_ for _ in ()).throw(module.ScholarFetchTimeoutError("timeout")),
    )

    with pytest.raises(SystemExit):
        module.get_scholar_citations()
