from __future__ import annotations
import argparse
import csv
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
import requests

from scrapers.books_scraper import scrape_books
from scrapers.quotes_scraper import scrape_quotes
from processing.cleaning import clean_record
from processing.validation import validate_record
from processing.deduplication import deduplicate

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
LOGS = ROOT / "logs"
SCHEMA = ["source", "source_url", "name_or_title", "category", "price", "rating", "author", "tags", "description", "availability", "author_url", "scraped_at"]


def configure_logging():
    LOGS.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.FileHandler(LOGS / "scraper.log", encoding="utf-8"), logging.StreamHandler()],
        force=True,
    )


def load_fixtures():
    with open(ROOT / "fixtures" / "sample_records.json", encoding="utf-8") as f:
        return json.load(f)


def run(use_fixture=False):
    started = time.perf_counter()
    configure_logging()
    session = requests.Session()
    session.headers.update({"User-Agent": "scraping-assignment/1.0 (educational project)"})
    scraped_at = datetime.now(timezone.utc).isoformat()
    raw_by_source = {"Books to Scrape": [], "Quotes to Scrape": []}
    failures = []

    if use_fixture:
        for r in load_fixtures():
            raw_by_source[r["source"]].append(r)
    else:
        for source, scraper in [("Books to Scrape", scrape_books), ("Quotes to Scrape", scrape_quotes)]:
            try:
                raw_by_source[source] = list(scraper(session))
            except Exception as exc:
                logging.exception("Source failed: %s", source)
                failures.append({"source": source, "error": str(exc)})

    raw = [r for records in raw_by_source.values() for r in records]
    cleaned = [clean_record(r, scraped_at) for r in raw]
    valid, rejected = [], []
    for record in cleaned:
        errors = validate_record(record)
        if errors:
            record["validation_errors"] = ";".join(errors)
            rejected.append(record)
        else:
            valid.append(record)

    unique, duplicates = deduplicate(valid)
    OUTPUT.mkdir(exist_ok=True)
    with open(OUTPUT / "final_dataset.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SCHEMA, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(unique)

    elapsed = round(time.perf_counter() - started, 3)
    summary = {
        "execution_time_seconds": elapsed,
        "records_collected": {source: len(records) for source, records in raw_by_source.items()},
        "total_records_collected": len(raw),
        "total_records_after_cleaning": len(cleaned),
        "records_rejected_during_validation": len(rejected),
        "duplicate_records_detected_or_removed": len(duplicates),
        "final_record_count": len(unique),
        "source_failures": failures,
        "validation_rejections": rejected,
    }
    with open(OUTPUT / "summary_report.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    logging.info("Finished: %s records in final dataset", len(unique))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-source scraping and consolidation pipeline")
    parser.add_argument("--fixture", action="store_true", help="Run against deterministic local fixture data")
    args = parser.parse_args()
    run(use_fixture=args.fixture)
