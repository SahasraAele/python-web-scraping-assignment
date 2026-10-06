from __future__ import annotations
from urllib.parse import urlparse

REQUIRED = ("source", "source_url", "name_or_title")


def validate_record(record):
    errors = []
    for field in REQUIRED:
        if not record.get(field):
            errors.append(f"missing:{field}")
    if record.get("price") is not None and not isinstance(record["price"], (int, float)):
        errors.append("invalid:price")
    if record.get("rating") is not None and record["rating"] not in range(1, 6):
        errors.append("invalid:rating")
    url = record.get("source_url")
    if url:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append("invalid:source_url")
    return errors
