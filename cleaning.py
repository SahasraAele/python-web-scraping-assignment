from __future__ import annotations
import re
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse


def clean_text(value):
    if value is None:
        return None
    if isinstance(value, list):
        return [clean_text(v) for v in value if clean_text(v)] or None
    value = re.sub(r"\s+", " ", str(value)).strip()
    return value or None


def clean_price(value):
    if value is None or value == "":
        return None
    cleaned = re.sub(r"[^0-9.\-]", "", str(value))
    try:
        return float(Decimal(cleaned))
    except (InvalidOperation, ValueError):
        return None


def clean_rating(value):
    if value is None or value == "":
        return None
    try:
        rating = int(value)
        return rating if 1 <= rating <= 5 else None
    except (TypeError, ValueError):
        return None


def normalize_url(value):
    if not value:
        return None
    value = str(value).strip()
    parsed = urlparse(value)
    return value if parsed.scheme in {"http", "https"} and parsed.netloc else None


def clean_record(record, scraped_at):
    cleaned = {key: clean_text(value) for key, value in record.items()}
    cleaned["price"] = clean_price(record.get("price"))
    cleaned["rating"] = clean_rating(record.get("rating"))
    cleaned["source_url"] = normalize_url(record.get("source_url"))
    cleaned["scraped_at"] = scraped_at
    if isinstance(cleaned.get("tags"), list):
        cleaned["tags"] = ", ".join(cleaned["tags"])
    return cleaned
