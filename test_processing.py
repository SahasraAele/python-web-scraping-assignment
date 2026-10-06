import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from processing.cleaning import clean_price, clean_text, clean_rating
from processing.deduplication import deduplicate
from processing.validation import validate_record


def test_cleaning():
    assert clean_text("  Hello   world ") == "Hello world"
    assert clean_price("£51.77") == 51.77
    assert clean_rating(5) == 5
    assert clean_rating(6) is None


def test_validation():
    record = {"source":"Books to Scrape","source_url":"https://example.com/a","name_or_title":"Book","price":10.5,"rating":4}
    assert validate_record(record) == []


def test_duplicate_detection_normalizes_title():
    base = {"source":"Books to Scrape","source_url":"https://example.com","name_or_title":"Example Book Title","author":None}
    other = {**base, "name_or_title":" EXAMPLE   BOOK TITLE "}
    unique, duplicates = deduplicate([base, other])
    assert len(unique) == 1
    assert len(duplicates) == 1
