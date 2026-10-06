from __future__ import annotations
import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
START_URL = BASE_URL
LOGGER = logging.getLogger(__name__)


def _text(node):
    return node.get_text(" ", strip=True) if node else None


def scrape_quotes(session: requests.Session, timeout: int = 20, max_retries: int = 3):
    url = START_URL
    page = 0
    while url:
        page += 1
        for attempt in range(1, max_retries + 1):
            try:
                response = session.get(url, timeout=timeout)
                response.raise_for_status()
                break
            except requests.RequestException as exc:
                LOGGER.warning("Quotes page %s attempt %s failed: %s", page, attempt, exc)
                if attempt == max_retries:
                    LOGGER.error("Skipping quotes page %s after %s attempts", page, max_retries)
                    response = None
        if response is None:
            url = None
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("div.quote")
        if not cards:
            LOGGER.warning("No quote cards found on %s", url)

        for card in cards:
            quote = card.select_one("span.text")
            author = card.select_one("small.author")
            author_link = card.select_one("span a")
            tags = [a.get_text(strip=True) for a in card.select("div.tags a.tag")]
            yield {
                "source": "Quotes to Scrape",
                "source_url": url,
                "name_or_title": _text(quote),
                "category": None,
                "price": None,
                "rating": None,
                "author": _text(author),
                "tags": tags or None,
                "description": None,
                "availability": None,
                "author_url": urljoin(url, author_link["href"]) if author_link else None,
            }

        next_link = soup.select_one("li.next a")
        url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
