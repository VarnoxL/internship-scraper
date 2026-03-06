from __future__ import annotations

from datetime import datetime
import csv
import json
from pathlib import Path
from typing import Iterable, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests import RequestException

from models import InternshipPosting


def fetch_html(url: str, timeout: int = 15) -> str:
    """Download the HTML for a given URL with simple error handling."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except RequestException as exc:
        raise RuntimeError(f"Failed to fetch URL '{url}': {exc}") from exc


def parse_internships(html: str, source: str, base_url: str = "") -> List[InternshipPosting]:
    """Parse internship rows from an HTML page into structured posting objects."""
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article.job-card, div.job-card, li.job-card")

    if not cards:
        cards = soup.select("article, div.listing, li.listing")

    postings: List[InternshipPosting] = []
    now = datetime.now()

    for card in cards:
        title_el = card.select_one("h2, h3, .job-title, .title")
        company_el = card.select_one(".company, .company-name")
        location_el = card.select_one(".location, .job-location")
        link_el = card.select_one("a[href]")

        if not title_el or not company_el or not link_el:
            continue

        title = title_el.get_text(strip=True)
        company = company_el.get_text(strip=True)
        location = (
            location_el.get_text(strip=True)
            if location_el
            else "Unknown"
        )

        href = link_el.get("href", "").strip()
        full_url = urljoin(base_url, href) if base_url else href
        tags = _infer_tags_from_text(f"{title} {company} {location}")

        posting = InternshipPosting(
            id="temp-id",
            source=source,
            company=company,
            title=title,
            location=location,
            is_remote="remote" in location.lower(),
            url=full_url,
            date_posted=None,
            scraped_at=now,
            tags=tags,
        )
        posting.id = posting.compute_id()
        postings.append(posting)

    return postings


def filter_postings(
    postings: Iterable[InternshipPosting],
    keywords: Iterable[str],
) -> List[InternshipPosting]:
    """Return only postings where any keyword appears in title/company/tags."""
    normalized_keywords = [word.lower() for word in keywords if word.strip()]
    if not normalized_keywords:
        return list(postings)

    filtered: List[InternshipPosting] = []
    for posting in postings:
        haystack = " ".join(
            [posting.title, posting.company,
                posting.location, " ".join(posting.tags)]
        ).lower()
        if any(keyword in haystack for keyword in normalized_keywords):
            filtered.append(posting)

    return filtered


def deduplicate_postings(postings: Iterable[InternshipPosting]) -> List[InternshipPosting]:
    """Remove duplicate postings based on their computed unique ID."""
    seen_ids = set()
    unique_postings = []
    for posting in postings:
        if posting.id not in seen_ids:
            seen_ids.add(posting.id)
            unique_postings.append(posting)
    return unique_postings


def export_to_csv(postings: Iterable[InternshipPosting], path: str | Path) -> None:
    """Export internship posting data to CSV."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "id",
                "source",
                "company",
                "title",
                "location",
                "is_remote",
                "url",
                "date_posted",
                "scraped_at",
                "tags",
            ],
        )
        writer.writeheader()
        for posting in postings:
            writer.writerow(
                {
                    "id": posting.id,
                    "source": posting.source,
                    "company": posting.company,
                    "title": posting.title,
                    "location": posting.location,
                    "is_remote": posting.is_remote,
                    "url": posting.url,
                    "date_posted": posting.date_posted.isoformat()
                    if posting.date_posted
                    else "",
                    "scraped_at": posting.scraped_at.isoformat(),
                    "tags": ",".join(posting.tags),
                }
            )


def export_to_json(postings: Iterable[InternshipPosting], path: str | Path) -> None:
    """Export internship posting data to JSON."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    serializable = []
    for posting in postings:
        serializable.append(
            {
                "id": posting.id,
                "source": posting.source,
                "company": posting.company,
                "title": posting.title,
                "location": posting.location,
                "is_remote": posting.is_remote,
                "url": posting.url,
                "date_posted": posting.date_posted.isoformat()
                if posting.date_posted
                else None,
                "scraped_at": posting.scraped_at.isoformat(),
                "tags": posting.tags,
            }
        )

    output.write_text(json.dumps(serializable, indent=2), encoding="utf-8")


def _infer_tags_from_text(text: str) -> List[str]:
    seed_terms = [
        "python",
        "intern",
        "software",
        "backend",
        "frontend",
        "data",
        "remote",
    ]
    lowered = text.lower()
    return [term for term in seed_terms if term in lowered]


def run_pipeline(
    url: str,
    source: str,
    keywords: Iterable[str],
    csv_path: str | Path = "output/internships.csv",
    json_path: str | Path = "output/internships.json",
) -> List[InternshipPosting]:
    html = fetch_html(url)
    postings = parse_internships(html, source=source, base_url=url)
    filtered = filter_postings(postings, keywords)
    unique = deduplicate_postings(filtered)

    export_to_csv(unique, csv_path)
    export_to_json(unique, json_path)
    return unique


def _demo_html() -> str:
    return """
    <html>
      <body>
        <article class='job-card'>
          <h2>Python Software Engineer Intern</h2>
          <div class='company'>Acme Corp</div>
          <div class='location'>Remote - US</div>
          <a href='/jobs/1'>Apply</a>
        </article>
        <article class='job-card'>
          <h2>Marketing Intern</h2>
          <div class='company'>Bright Media</div>
          <div class='location'>New York, NY</div>
          <a href='/jobs/2'>Apply</a>
        </article>
      </body>
    </html>
    """


def main() -> None:
    """Run a local demo parse + export flow."""
    source = "demo-board"
    keywords = ["Python", "Intern"]

    postings = parse_internships(
        _demo_html(), source=source, base_url="https://example.com")
    filtered = filter_postings(postings, keywords)
    unique = deduplicate_postings(filtered)

    export_to_csv(unique, "output/internships.csv")
    export_to_json(unique, "output/internships.json")

    print(
        f"Parsed {len(postings)} postings and kept {len(unique)} after filtering.")


if __name__ == "__main__":
    main()
