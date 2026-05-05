#!/usr/bin/env python

from __future__ import annotations

import os
import re
import signal
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import yaml
from scholarly import scholarly

CONFIG_FILE = Path("_data/socials.yml")
OUTPUT_FILE = Path("_data/citations.yml")
BIBLIOGRAPHY_FILE = Path("_bibliography/papers.bib")
FETCH_TIMEOUT_SECONDS = int(os.getenv("SCHOLAR_FETCH_TIMEOUT_SECONDS", "60"))
PUBLICATION_FETCH_TIMEOUT_SECONDS = int(
    os.getenv("SCHOLAR_PUBLICATION_FETCH_TIMEOUT_SECONDS", "15")
)
ALLOW_STALE_ON_FETCH_FAILURE = (
    os.getenv("ALLOW_STALE_CITATIONS_ON_FETCH_FAILURE", "1") != "0"
)
CITED_BY_REGEX = re.compile(r"Cited by\s+(\d[\d,]*)")


class ScholarFetchTimeoutError(TimeoutError):
    """Raised when fetching Scholar data exceeds the internal deadline."""


def load_scholar_user_id(config_file: Path = CONFIG_FILE) -> str:
    """
    Load the Google Scholar user ID from the configuration file.

    Parameters
    ----------
    config_file : Path
        Path to the socials configuration file.

    Returns
    -------
    str
        Google Scholar user identifier.
    """
    if not config_file.exists():
        print(
            "Configuration file "
            f"{config_file} not found. Please ensure the file exists and "
            "contains your Google Scholar user ID."
        )
        sys.exit(1)
    try:
        with config_file.open() as file_handle:
            config = yaml.safe_load(file_handle)
        scholar_user_id = config.get("scholar_userid")
        if not scholar_user_id:
            print(
                "No 'scholar_userid' found in the configuration file. "
                "Please add 'scholar_userid' to _data/socials.yml."
            )
            sys.exit(1)
        return scholar_user_id
    except yaml.YAMLError as error:
        print(
            f"Error parsing YAML file {config_file}: {error}. "
            "Please check the file for correct YAML syntax."
        )
        sys.exit(1)


def load_existing_citations(output_file: Path | None = None) -> dict[str, Any] | None:
    """
    Load the current citation cache if it exists.

    Parameters
    ----------
    output_file : Path
        Path to the citation cache file.

    Returns
    -------
    dict[str, Any] | None
        Parsed citation data when present and readable.
    """
    if output_file is None:
        output_file = OUTPUT_FILE

    if not output_file.exists():
        return None

    try:
        with output_file.open() as file_handle:
            return yaml.safe_load(file_handle)
    except Exception as error:
        print(
            "Warning: Could not read existing citation data from "
            f"{output_file}: {error}. The file may be missing or corrupted."
        )
        return None


@contextmanager
def fetch_deadline(seconds: int):
    """
    Enforce an internal deadline for Scholar network calls.

    Parameters
    ----------
    seconds : int
        Maximum allowed runtime for the wrapped section.
    """
    if seconds <= 0 or os.name == "nt":
        yield
        return

    def _handle_timeout(signum: int, frame: Any) -> None:
        raise ScholarFetchTimeoutError(
            f"Timed out after {seconds} seconds while fetching Google Scholar data."
        )

    previous_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, _handle_timeout)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)


def fetch_author_data(scholar_user_id: str) -> dict[str, Any]:
    """
    Fetch author details from Google Scholar.

    Parameters
    ----------
    scholar_user_id : str
        Google Scholar author identifier.

    Returns
    -------
    dict[str, Any]
        Author payload including publications.
    """
    scholarly.set_timeout(15)
    scholarly.set_retries(1)
    with fetch_deadline(FETCH_TIMEOUT_SECONDS):
        author = scholarly.search_author_id(scholar_user_id)
        return cast(
            dict[str, Any],
            scholarly.fill(cast(dict[str, Any], author), sections=["publications"]),
        )


def build_citation_data(
    author_data: dict[str, Any], today: str
) -> dict[str, dict[str, Any] | str]:
    """
    Convert author publication data into the stored citation structure.

    Parameters
    ----------
    author_data : dict[str, Any]
        Author payload returned by `scholarly`.
    today : str
        Update date in ISO format.

    Returns
    -------
    dict[str, dict[str, Any] | str]
        Citation payload ready to serialize.
    """
    citation_data: dict[str, Any] = {"metadata": {"last_updated": today}, "papers": {}}

    for pub in author_data["publications"]:
        try:
            pub_id = pub.get("pub_id") or pub.get("author_pub_id")
            if not pub_id:
                title = pub.get("bib", {}).get("title", "Unknown")
                print(
                    "Warning: No ID found for publication: "
                    f"{title}. This publication will be skipped."
                )
                continue

            title = pub.get("bib", {}).get("title", "Unknown Title")
            year = pub.get("bib", {}).get("pub_year", "Unknown Year")
            citations = pub.get("num_citations", 0)

            print(f"Found: {title} ({year}) - Citations: {citations}")

            citation_data["papers"][pub_id] = {
                "title": title,
                "year": year,
                "citations": citations,
            }
        except Exception as error:
            title = pub.get("bib", {}).get("title", "Unknown")
            print(
                f"Error processing publication '{title}': {error}. "
                "This publication will be skipped."
            )

    return citation_data


def parse_bibliography_entries(
    bibliography_file: Path | None = None,
) -> list[dict[str, str]]:
    """
    Parse the BibTeX fields needed for citation updates.

    Parameters
    ----------
    bibliography_file : Path | None
        BibTeX bibliography file. Defaults to `_bibliography/papers.bib`.

    Returns
    -------
    list[dict[str, str]]
        Parsed BibTeX entries keyed by lowercase field name.
    """
    if bibliography_file is None:
        bibliography_file = BIBLIOGRAPHY_FILE

    text = bibliography_file.read_text()
    entries: list[dict[str, str]] = []
    index = 0

    while True:
        at_index = text.find("@", index)
        if at_index == -1:
            break

        open_index = _find_entry_open(text, at_index)
        if open_index == -1:
            break

        close_index = _find_matching_brace(text, open_index)
        if close_index == -1:
            break

        entry_body = text[open_index + 1 : close_index]
        entries.append(_parse_bibtex_fields(entry_body))
        index = close_index + 1

    return entries


def _find_entry_open(text: str, start: int) -> int:
    for index in range(start, len(text)):
        if text[index] in "{(":
            return index
        if text[index] == "\n":
            return -1
    return -1


def _find_matching_brace(text: str, open_index: int) -> int:
    opener = text[open_index]
    closer = "}" if opener == "{" else ")"
    depth = 0
    for index in range(open_index, len(text)):
        char = text[index]
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return index
    return -1


def _parse_bibtex_fields(entry_body: str) -> dict[str, str]:
    first_comma = entry_body.find(",")
    if first_comma == -1:
        return {}

    fields_text = entry_body[first_comma + 1 :]
    fields: dict[str, str] = {}
    index = 0

    while index < len(fields_text):
        while index < len(fields_text) and fields_text[index] in " \t\r\n,":
            index += 1

        name_start = index
        while index < len(fields_text) and (
            fields_text[index].isalnum() or fields_text[index] in "_-"
        ):
            index += 1

        field_name = fields_text[name_start:index].strip().lower()
        while index < len(fields_text) and fields_text[index].isspace():
            index += 1

        if not field_name or index >= len(fields_text) or fields_text[index] != "=":
            index += 1
            continue

        index += 1
        while index < len(fields_text) and fields_text[index].isspace():
            index += 1

        value, index = _read_bibtex_value(fields_text, index)
        fields[field_name] = value.strip()

    return fields


def _read_bibtex_value(text: str, start: int) -> tuple[str, int]:
    if start >= len(text):
        return "", start

    if text[start] == "{":
        close_index = _find_matching_brace(text, start)
        if close_index == -1:
            return text[start + 1 :].strip(), len(text)
        return text[start + 1 : close_index].strip(), close_index + 1

    if text[start] == '"':
        index = start + 1
        while index < len(text):
            if text[index] == '"' and text[index - 1] != "\\":
                return text[start + 1 : index].strip(), index + 1
            index += 1
        return text[start + 1 :].strip(), len(text)

    index = start
    while index < len(text) and text[index] not in ",\n":
        index += 1
    return text[start:index].strip(), index


def fetch_publication_citation_count(scholar_user_id: str, publication_id: str) -> int:
    """
    Fetch a citation count from a publication's Google Scholar page.

    Parameters
    ----------
    scholar_user_id : str
        Google Scholar author identifier.
    publication_id : str
        Per-publication Google Scholar identifier from the BibTeX entry.

    Returns
    -------
    int
        Citation count found on the publication page, or 0 when absent.
    """
    query = urlencode(
        {
            "view_op": "view_citation",
            "hl": "en",
            "user": scholar_user_id,
            "citation_for_view": f"{scholar_user_id}:{publication_id}",
        }
    )
    request = Request(
        f"https://scholar.google.com/citations?{query}",
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        },
    )

    with urlopen(request, timeout=PUBLICATION_FETCH_TIMEOUT_SECONDS) as response:
        html = response.read().decode("utf-8", errors="replace")

    match = CITED_BY_REGEX.search(html)
    if not match:
        return 0
    return int(match.group(1).replace(",", ""))


def build_bibliography_citation_data(
    scholar_user_id: str, today: str
) -> dict[str, dict[str, Any] | str]:
    """
    Build citation data by reading publication IDs from the bibliography.

    Parameters
    ----------
    scholar_user_id : str
        Google Scholar author identifier.
    today : str
        Update date in ISO format.

    Returns
    -------
    dict[str, dict[str, Any] | str]
        Citation payload ready to serialize.
    """
    citation_data: dict[str, Any] = {"metadata": {"last_updated": today}, "papers": {}}
    errors: list[str] = []

    for entry in parse_bibliography_entries():
        publication_id = entry.get("google_scholar_id")
        if not publication_id:
            continue

        title = entry.get("title", "Unknown Title")
        year = entry.get("year", "Unknown Year")
        try:
            citations = fetch_publication_citation_count(
                scholar_user_id, publication_id
            )
        except Exception as error:
            errors.append(f"{publication_id}: {error}")
            print(
                "Warning: Could not fetch citation count for publication "
                f"{publication_id}: {error}. This publication will be skipped."
            )
            continue

        print(f"Found: {title} ({year}) - Citations: {citations}")
        citation_data["papers"][f"{scholar_user_id}:{publication_id}"] = {
            "title": title,
            "year": year,
            "citations": citations,
        }

    if not citation_data["papers"]:
        detail = "; ".join(errors) if errors else "No google_scholar_id entries found."
        raise RuntimeError(f"Could not build citation data from bibliography. {detail}")

    return citation_data


def get_scholar_citations() -> None:
    """
    Fetch and update Google Scholar citation data.

    Returns
    -------
    None
        This function writes `_data/citations.yml` when data changes.
    """
    scholar_user_id = load_scholar_user_id()
    print(f"Fetching citations for Google Scholar ID: {scholar_user_id}")
    today = datetime.now().strftime("%Y-%m-%d")
    existing_data = load_existing_citations()

    if (
        existing_data
        and "metadata" in existing_data
        and "last_updated" in existing_data["metadata"]
    ):
        print(f"Last updated on: {existing_data['metadata']['last_updated']}")
        if existing_data["metadata"]["last_updated"] == today:
            print("Citations data is already up-to-date. Skipping fetch.")
            return

    try:
        author_data = fetch_author_data(scholar_user_id)
        if not author_data:
            print(
                f"Could not fetch author data for user ID '{scholar_user_id}'. "
                "Please verify the Scholar user ID and try again."
            )
            sys.exit(1)

        if "publications" not in author_data:
            print(
                f"No publications found in author data for user ID '{scholar_user_id}'."
            )
            sys.exit(1)

        citation_data = build_citation_data(author_data, today)
    except (ScholarFetchTimeoutError, Exception) as error:
        print(
            "Warning: Could not refresh citations from the Google Scholar author "
            f"profile for user ID '{scholar_user_id}': {error}. Trying the "
            "bibliography publication pages instead."
        )
        try:
            citation_data = build_bibliography_citation_data(scholar_user_id, today)
        except Exception as fallback_error:
            if ALLOW_STALE_ON_FETCH_FAILURE and existing_data:
                print(
                    "Warning: Could not refresh Google Scholar citations for "
                    f"user ID '{scholar_user_id}'. Author profile error: {error}. "
                    f"Bibliography fallback error: {fallback_error}. Keeping the "
                    "existing citation data."
                )
                return
            print(
                "Error fetching citation data from Google Scholar for user ID "
                f"'{scholar_user_id}'. Author profile error: {error}. "
                f"Bibliography fallback error: {fallback_error}."
            )
            sys.exit(1)

    if existing_data and existing_data.get("papers") == citation_data["papers"]:
        print("No changes in citation data. Skipping file update.")
        return

    try:
        with OUTPUT_FILE.open("w") as file_handle:
            yaml.dump(citation_data, file_handle, width=1000, sort_keys=True)
        print(f"Citation data saved to {OUTPUT_FILE}")
    except Exception as error:
        print(
            f"Error writing citation data to {OUTPUT_FILE}: {error}. "
            "Please check file permissions and disk space."
        )
        sys.exit(1)


if __name__ == "__main__":
    try:
        get_scholar_citations()
    except Exception as error:
        print(f"Unexpected error: {error}")
        sys.exit(1)
