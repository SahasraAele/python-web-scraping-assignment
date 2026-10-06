from __future__ import annotations
import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
START_URL = urljoin(BASE_URL, "catalogue/page-1.html")
LOGGER = logging.getLogger(__name__)


def _text(node):
    return node.get_text(" ", strip=True) if node else None


def _rating(card):
    tag = card.select_one("p.star-rating")
    if not tag:
        return None
    classes = tag.get("class", [])
    names = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    return next((names[c] for c in classes if c in names), None)


def scrape_books(session: requests.Session, timeout: int = 20, max_retries: int = 3):
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
                LOGGER.warning("Books page %s attempt %s failed: %s", page, attempt, exc)
                if attempt == max_retries:
                    LOGGER.error("Skipping books page %s after %s attempts", page, max_retries)
                    response = None
        if response is None:
            url = None
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("article.product_pod")
        if not cards:
            LOGGER.warning("No book cards found on %s", url)

        for card in cards:
            link = card.select_one("h3 a")
            yield {
                "source": "Books to Scrape",
                "source_url": urljoin(url, link.get("href")) if link else url,
                "name_or_title": link.get("title") if link else _text(card.select_one("h3")),
                "category": None,
                "price": _text(card.select_one("p.price_color")),
                "rating": _rating(card),
                "author": None,
                "tags": None,
                "description": None,
                "availability": _text(card.select_one("p.instock")),
            }

        next_link = soup.select_one("li.next a")
        url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
