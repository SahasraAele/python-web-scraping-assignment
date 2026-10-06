# AI_USAGE.md

## Tool used

**ChatGPT**

## What AI was used for

- Translating the assessment requirements into a clean Python project structure.
- Designing a common record schema for both sources.
- Drafting Requests + BeautifulSoup pagination logic.
- Designing reusable cleaning, validation and deduplication functions.
- Drafting unit tests for data processing behavior.
- Reviewing error-handling and documentation requirements.

## Representative prompts

1. "Build a Python multi-source scraper with separate Books to Scrape and Quotes to Scrape modules, automatic pagination, and a shared schema."
2. "Add reusable text, price, rating and URL cleaning functions and validation rules."
3. "Implement duplicate detection that is robust to whitespace and capitalization differences."
4. "Create pytest tests for cleaning, validation and duplicate detection."
5. "Write README and AI usage documentation covering setup, pagination, assumptions, limitations and outputs."

## AI-assisted areas

The initial project architecture, scraper skeletons, processing functions, tests and documentation were AI-assisted. The final project is organized so each source-specific parser and each transformation stage can be inspected independently.

## Review and changes

Important implementation decisions were reviewed against the assignment requirements:

- Pagination follows the site's `next` link rather than a fixed page count.
- Missing elements return null values instead of invented content.
- Price and rating conversion happens in the processing layer rather than inside source selectors.
- Deduplication normalizes Unicode/case/whitespace/punctuation and includes source in the key.
- Request failures are retried and then logged/skipped so one page does not terminate the full pipeline.
- Validation failures are counted in the summary report.

## Verification

Run:

```bash
pytest -q
python main.py --fixture
```

For final live verification, run `python main.py` from a machine with internet access and inspect `output/final_dataset.csv`, `output/summary_report.json`, and `logs/scraper.log`.

## Important note

AI output is not treated as authoritative. The candidate remains responsible for understanding the code, checking selectors, and verifying the final results before submission.
