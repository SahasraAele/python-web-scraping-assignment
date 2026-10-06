from __future__ import annotations
import re
import unicodedata


def normalize_key(value):
    value = unicodedata.normalize("NFKC", str(value or ""))
    value = value.casefold()
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"[^\w\s]", "", value)
    return value


def duplicate_key(record):
    # Source is included so identical text from two unrelated sites is not lost.
    return (
        normalize_key(record.get("source")),
        normalize_key(record.get("name_or_title")),
        normalize_key(record.get("author")),
    )


def deduplicate(records):
    seen = set()
    unique = []
    duplicates = []
    for record in records:
        key = duplicate_key(record)
        if key in seen:
            duplicates.append(record)
        else:
            seen.add(key)
            unique.append(record)
    return unique, duplicates
