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
    monkeypatch.setattr(
        module,
        "build_bibliography_citation_data",
        lambda scholar_user_id, update_date: (_ for _ in ()).throw(
            RuntimeError("fallback failed")
        ),
    )

    module.get_scholar_citations()

    assert yaml.safe_load(citation_path.read_text()) == original_payload


def test_uses_bibliography_fallback_when_author_fetch_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = load_module()
    today = "2026-03-27"
    citation_path = tmp_path / "citations.yml"
    citation_path.write_text(
        yaml.safe_dump(
            {
                "metadata": {"last_updated": "2026-03-20"},
                "papers": {
                    "abc123:old": {
                        "title": "Existing",
                        "year": "2024",
                        "citations": 3,
                    }
                },
            }
        )
    )
    fallback_payload = {
        "metadata": {"last_updated": today},
        "papers": {
            "abc123:new": {
                "title": "Updated",
                "year": "2026",
                "citations": 8,
            }
        },
    }

    monkeypatch.setattr(module, "OUTPUT_FILE", citation_path)
    monkeypatch.setattr(module, "ALLOW_STALE_ON_FETCH_FAILURE", True)
    monkeypatch.setattr(module, "load_scholar_user_id", lambda: "abc123")
    set_today(monkeypatch, module, today)
    monkeypatch.setattr(
        module,
        "fetch_author_data",
        lambda _: (_ for _ in ()).throw(module.ScholarFetchTimeoutError("timeout")),
    )
    monkeypatch.setattr(
        module,
        "build_bibliography_citation_data",
        lambda scholar_user_id, update_date: fallback_payload,
    )

    module.get_scholar_citations()

    assert yaml.safe_load(citation_path.read_text()) == fallback_payload


def test_builds_bibliography_citation_data_from_google_scholar_ids(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = load_module()
    bibliography_path = tmp_path / "papers.bib"
    bibliography_path.write_text(
        """
@article{paper1,
  title = {{Nested} Title},
  year = {2026},
  google_scholar_id = {paper-one},
}

@inproceedings{paper2,
  title = {Second Paper},
  year = {2024},
  google_scholar_id = {paper-two},
}
""".strip()
    )

    monkeypatch.setattr(module, "BIBLIOGRAPHY_FILE", bibliography_path)
    monkeypatch.setattr(
        module,
        "fetch_publication_citation_count",
        lambda scholar_user_id, publication_id: {
            "paper-one": 12,
            "paper-two": 3,
        }[publication_id],
    )

    citation_data = module.build_bibliography_citation_data("abc123", "2026-03-27")

    assert citation_data == {
        "metadata": {"last_updated": "2026-03-27"},
        "papers": {
            "abc123:paper-one": {
                "title": "{Nested} Title",
                "year": "2026",
                "citations": 12,
            },
            "abc123:paper-two": {
                "title": "Second Paper",
                "year": "2024",
                "citations": 3,
            },
        },
    }


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
    monkeypatch.setattr(
        module,
        "build_bibliography_citation_data",
        lambda scholar_user_id, update_date: (_ for _ in ()).throw(
            RuntimeError("fallback failed")
        ),
    )

    with pytest.raises(SystemExit):
        module.get_scholar_citations()
