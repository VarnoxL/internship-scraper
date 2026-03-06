# Internship Web Scraper Application (In Progress)

A Python-based internship scraper that extracts job listing data from HTML pages, filters for relevant software roles, and exports cleaned datasets for analysis.

## Features

- Scrapes internship listings using `requests` + `BeautifulSoup`.
- Parses structured fields:
  - Job title
  - Company
  - Location
  - Posting URL
- Adds keyword-based filtering (e.g., `Python`, `Intern`) to find software-relevant roles.
- Exports results to:
  - CSV (`output/internships.csv`)
  - JSON (`output/internships.json`)
- Uses reusable functions and basic error handling for reliability.

## Project Structure

- `main.py` – scraping pipeline, parsing, filtering, export utilities, and demo runner.
- `models.py` – Pydantic data model for internship postings.

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

The demo run parses sample HTML and writes output files to the `output/` folder.

## Notes

- Parsing selectors are intentionally generic (`.job-card`, `.company`, `.location`) so you can adapt them per target site.
- For real usage, call `run_pipeline(url, source, keywords)` from `main.py` with an actual job board URL.
