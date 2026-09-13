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


WORKFLOW_PATH = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "update-citations.yml"
)


def _workflow_script_step_env() -> dict[str, str]:
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text())
    steps = workflow["jobs"]["update-citations"]["steps"]
    step = next(s for s in steps if s.get("id") == "run_citation_update")
    return step["env"]


def test_workflow_stale_flag_is_read_by_script(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env = _workflow_script_step_env()
    assert env["ALLOW_STALE_ON_FETCH_FAILURE"] == "0"

    monkeypatch.setenv("ALLOW_STALE_ON_FETCH_FAILURE", "0")
    module = load_module()
    assert module.ALLOW_STALE_ON_FETCH_FAILURE is False

    monkeypatch.setenv("ALLOW_STALE_ON_FETCH_FAILURE", "1")
    module = load_module()
    assert module.ALLOW_STALE_ON_FETCH_FAILURE is True


def test_exits_when_stale_not_allowed_and_fetch_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("ALLOW_STALE_ON_FETCH_FAILURE", "0")
    module = load_module()
    output_file = tmp_path / "citations.yml"
    existing = {
        "metadata": {"last_updated": "2026-03-20"},
        "papers": {"abc123:pub1": {"title": "T", "year": "2024", "citations": 3}},
    }
    output_file.write_text(yaml.safe_dump(existing))
    monkeypatch.setattr(module, "OUTPUT_FILE", output_file)
    monkeypatch.setattr(module, "load_scholar_user_id", lambda: "abc123")
    set_today(monkeypatch, module)
    monkeypatch.setattr(
        module,
        "fetch_author_data",
        lambda _: (_ for _ in ()).throw(RuntimeError("Cannot Fetch")),
    )
    monkeypatch.setattr(
        module,
        "build_bibliography_citation_data",
        lambda scholar_user_id, update_date: (_ for _ in ()).throw(
            RuntimeError("HTTP Error 403: Forbidden")
        ),
    )

    with pytest.raises(SystemExit) as exc_info:
        module.get_scholar_citations()

    assert exc_info.value.code == 1
    assert yaml.safe_load(output_file.read_text()) == existing


REQUIREMENTS_PATH = Path(__file__).resolve().parents[1] / "requirements.txt"


class _FakeResponse:
    def __init__(self, body: str) -> None:
        self.body = body
        self.status = 200

    def read(self) -> bytes:
        return self.body.encode()

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None


def test_workflow_passes_scraperapi_secret_to_script() -> None:
    env = _workflow_script_step_env()
    assert env["SCRAPERAPI_KEY"] == "${{ secrets.SCRAPERAPI_KEY }}"


def test_requirements_pin_httpx_for_scholarly_proxy() -> None:
    lines = [line.strip() for line in REQUIREMENTS_PATH.read_text().splitlines()]
    assert "httpx<0.28" in lines


def test_fallback_fetch_goes_direct_without_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module()
    monkeypatch.setattr(module, "SCRAPERAPI_KEY", "")
    seen: dict[str, object] = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        return _FakeResponse("<div>Cited by 7</div>")

    monkeypatch.setattr(module, "urlopen", fake_urlopen)

    assert module.fetch_publication_citation_count("abc123", "pub1") == 7
    assert str(seen["url"]).startswith("https://scholar.google.com/citations?")
    assert seen["timeout"] == module.PUBLICATION_FETCH_TIMEOUT_SECONDS


def test_fallback_fetch_goes_through_scraperapi_with_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from urllib.parse import parse_qs, urlsplit

    module = load_module()
    monkeypatch.setattr(module, "SCRAPERAPI_KEY", "secret-key")
    seen: dict[str, object] = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        return _FakeResponse("<div>Cited by 1,234</div>")

    monkeypatch.setattr(module, "urlopen", fake_urlopen)

    assert module.fetch_publication_citation_count("abc123", "pub1") == 1234
    parts = urlsplit(str(seen["url"]))
    assert (
        f"{parts.scheme}://{parts.netloc}{parts.path}" == "https://api.scraperapi.com/"
    )
    query = parse_qs(parts.query)
    assert query["api_key"] == ["secret-key"]
    target = urlsplit(query["url"][0])
    assert target.netloc == "scholar.google.com"
    assert parse_qs(target.query)["citation_for_view"] == ["abc123:pub1"]
    assert seen["timeout"] == module.SCRAPERAPI_TIMEOUT_SECONDS


def test_configure_scholar_proxy_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_module()
    monkeypatch.setattr(module, "SCRAPERAPI_KEY", "")
    monkeypatch.setattr(
        module,
        "ProxyGenerator",
        lambda: (_ for _ in ()).throw(AssertionError("must not build a proxy")),
    )

    assert module.configure_scholar_proxy() is False


def test_configure_scholar_proxy_with_key(monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_module()
    monkeypatch.setattr(module, "SCRAPERAPI_KEY", "secret-key")
    calls: dict[str, object] = {}

    class FakeProxyGenerator:
        def ScraperAPI(self, api_key: str) -> bool:  # noqa: N802
            calls["api_key"] = api_key
            return True

    class FakeScholarly:
        def use_proxy(self, proxy_generator) -> None:
            calls["use_proxy"] = proxy_generator

        def set_timeout(self, timeout: int) -> None:
            calls["timeout"] = timeout

    monkeypatch.setattr(module, "ProxyGenerator", FakeProxyGenerator)
    monkeypatch.setattr(module, "scholarly", FakeScholarly())
    monkeypatch.setattr(module, "report_scraperapi_usage", lambda: None)

    assert module.configure_scholar_proxy() is True
    assert calls["api_key"] == "secret-key"
    assert isinstance(calls["use_proxy"], FakeProxyGenerator)
    assert calls["timeout"] == module.SCRAPERAPI_TIMEOUT_SECONDS


def test_configure_scholar_proxy_falls_back_when_setup_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module()
    monkeypatch.setattr(module, "SCRAPERAPI_KEY", "secret-key")

    class FakeProxyGenerator:
        def ScraperAPI(self, api_key: str) -> bool:  # noqa: N802
            return False

    class FakeScholarly:
        def use_proxy(self, proxy_generator) -> None:
            raise AssertionError("must not use a broken proxy")

    monkeypatch.setattr(module, "ProxyGenerator", FakeProxyGenerator)
    monkeypatch.setattr(module, "scholarly", FakeScholarly())

    assert module.configure_scholar_proxy() is False


def test_report_scraperapi_usage_prints_counts(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = load_module()
    monkeypatch.setattr(module, "SCRAPERAPI_KEY", "secret-key")
    monkeypatch.setattr(
        module,
        "urlopen",
        lambda request, timeout: _FakeResponse(
            '{"requestCount": 42, "requestLimit": 1000}'
        ),
    )

    module.report_scraperapi_usage()

    out = capsys.readouterr().out
    assert "42 / 1000" in out
    assert "secret-key" not in out


def test_force_refresh_fetches_even_when_updated_today(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SCHOLAR_FORCE_REFRESH", "1")
    module = load_module()
    output_file = tmp_path / "citations.yml"
    output_file.write_text(
        yaml.safe_dump({"metadata": {"last_updated": "2026-03-27"}, "papers": {}})
    )
    monkeypatch.setattr(module, "OUTPUT_FILE", output_file)
    monkeypatch.setattr(module, "load_scholar_user_id", lambda: "abc123")
    set_today(monkeypatch, module, "2026-03-27")
    monkeypatch.setattr(
        module,
        "fetch_author_data",
        lambda _: {
            "publications": [
                {
                    "author_pub_id": "abc123:pub1",
                    "bib": {"title": "T", "pub_year": "2024"},
                    "num_citations": 5,
                }
            ]
        },
    )

    module.get_scholar_citations()

    saved = yaml.safe_load(output_file.read_text())
    assert saved["papers"]["abc123:pub1"]["citations"] == 5


def test_workflow_dispatch_exposes_force_refresh_input() -> None:
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text())
    inputs = workflow[True]["workflow_dispatch"]["inputs"]
    assert inputs["force_refresh"]["type"] == "boolean"
    env = _workflow_script_step_env()
    assert "force_refresh" in env["SCHOLAR_FORCE_REFRESH"]
