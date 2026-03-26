#!/usr/bin/env python

from __future__ import annotations

import os
import signal
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import yaml
from scholarly import scholarly

CONFIG_FILE = Path("_data/socials.yml")
OUTPUT_FILE = Path("_data/citations.yml")
FETCH_TIMEOUT_SECONDS = int(os.getenv("SCHOLAR_FETCH_TIMEOUT_SECONDS", "60"))
ALLOW_STALE_ON_FETCH_FAILURE = (
    os.getenv("ALLOW_STALE_CITATIONS_ON_FETCH_FAILURE", "1") != "0"
)


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
    except (ScholarFetchTimeoutError, Exception) as error:
        if ALLOW_STALE_ON_FETCH_FAILURE and existing_data:
            print(
                "Warning: Could not refresh Google Scholar citations for "
                f"user ID '{scholar_user_id}': {error}. Keeping the existing "
                "citation data."
            )
            return
        print(
            "Error fetching author data from Google Scholar for user ID "
            f"'{scholar_user_id}': {error}. Please check your internet "
            "connection and Scholar user ID."
        )
        sys.exit(1)

    if not author_data:
        print(
            f"Could not fetch author data for user ID '{scholar_user_id}'. "
            "Please verify the Scholar user ID and try again."
        )
        sys.exit(1)

    if "publications" not in author_data:
        print(f"No publications found in author data for user ID '{scholar_user_id}'.")
        sys.exit(1)

    citation_data = build_citation_data(author_data, today)

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
