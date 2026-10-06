# Multi-Source Web Scraping & Data Consolidation

## Overview

This project implements the take-home assessment using Python, Requests and BeautifulSoup. It scrapes **Books to Scrape** and **Quotes to Scrape**, follows pagination automatically, maps both sources into a shared schema, cleans and validates records, detects normalized duplicates, and writes a consolidated CSV plus JSON summary.

## Python version

Python 3.10+ recommended (tested design target: Python 3.11+).

## Installation

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Run the live scraper

```bash
python main.py
```

The scraper uses reasonable request timeouts, a descriptive User-Agent, retries failed pages, logs errors, and continues to the next source/page when a page cannot be processed.

## Run the deterministic local fixture/demo

```bash
python main.py --fixture
```

This mode is useful for reviewers and automated tests because it does not depend on internet availability. The fixture intentionally contains a duplicate title with different whitespace/capitalization to demonstrate the deduplication rule.

## Run tests

```bash
pytest -q
```

## Project structure

```text
scraping_assignment/
├── scrapers/
│   ├── books_scraper.py
│   └── quotes_scraper.py
├── processing/
│   ├── cleaning.py
│   ├── validation.py
│   └── deduplication.py
├── fixtures/
│   └── sample_records.json
├── output/
│   ├── final_dataset.csv
│   └── summary_report.json
├── logs/
│   └── scraper.log
├── tests/
│   └── test_processing.py
├── main.py
├── requirements.txt
├── README.md
└── AI_USAGE.md
```

## Pagination

Books to Scrape starts at `/catalogue/page-1.html`; the scraper reads the `li.next a` link and keeps following it until there is no next link. Quotes to Scrape follows the same idea with its `li.next a` navigation. No fixed page count is hard-coded.

## Data model

The common schema is:

- `source`
- `source_url`
- `name_or_title`
- `category`
- `price`
- `rating`
- `author`
- `tags`
- `description`
- `availability`
- `author_url`
- `scraped_at`

Fields unavailable for a source are represented as null/empty values rather than invented values.

## Cleaning

Cleaning is separated from scraping. Text whitespace is normalized, prices are converted to numeric floats, ratings are constrained to 1–5, URLs are checked for HTTP/HTTPS structure, and tag lists are converted to comma-separated text.

## Validation

A valid record requires `source`, `source_url`, and `name_or_title`. Optional numeric values are checked for valid types/ranges and URLs are checked for a valid scheme and hostname. Invalid records are counted and retained in the summary for auditability.

## Deduplication

Duplicate keys are built from normalized `source + name_or_title + author`. Unicode normalization, case-folding, whitespace normalization, and punctuation removal make comparisons robust to common formatting differences. Source is part of the key so unrelated records from different sites are not accidentally merged.

## Error handling

Request failures are retried up to three times. A page that still fails is logged and skipped instead of stopping the entire run. Missing HTML elements produce null fields rather than crashing the pipeline.

## Output

- `output/final_dataset.csv`: standardized consolidated records.
- `output/summary_report.json`: collection, rejection, duplicate, final-count and execution-time metrics.
- `logs/scraper.log`: execution and error logs.

## Assumptions

1. The supplied sites remain publicly accessible and retain compatible HTML selectors.
2. The assignment's suggested common schema is sufficient for both sources.
3. A duplicate means the same normalized source/title/author combination.
4. No data is invented when a field does not exist in a source.

## Known limitations

- The live pipeline intentionally does not scrape individual book detail pages, so source-specific fields only visible on detail pages (such as full category/description) remain null. This keeps the solution focused on the required multi-page listing workflow.
- Websites can change HTML structures; selectors are therefore isolated in source modules.
- The fixture output is a deterministic demonstration, not a replacement for a live run.

## AI usage

See `AI_USAGE.md`. AI assistance was used for initial architecture, implementation drafting, test design and documentation; the implementation should still be reviewed and explained by the candidate.
