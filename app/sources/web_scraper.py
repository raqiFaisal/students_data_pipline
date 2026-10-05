from __future__ import annotations

import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

from app.utils.logger import get_logger

logger = get_logger()


def extract_web_table(
    url: str,
    table_selector: str = "table",
    row_selector: str = "tbody tr",
    header_selector: str = "th",
    cell_selector: str = "td",
    timeout: int = 10,
) -> pd.DataFrame:
    """Scrape an HTML table and return the result as a pandas DataFrame.

    CSS selectors are configurable so the scraper can be adapted to a real
    website without changing Python code. Connection and parsing failures are
    logged and return an empty DataFrame so optional scraping does not stop the
    whole pipeline.
    """
    if not url:
        logger.warning("Web scraping skipped: URL is empty")
        return pd.DataFrame()

    logger.info("Scraping started: %s", url)

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; StudentDataPipeline/1.0)"
                )
            },
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Web scraping connection failed: %s", exc)
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.select_one(table_selector)

    if table is None:
        logger.warning("Web scraping found no table: %s", table_selector)
        return pd.DataFrame()

    header_nodes = table.select(header_selector)
    if not header_nodes:
        first_row = table.select_one("tr")
        header_nodes = first_row.select(cell_selector) if first_row else []

    headers = [_normalize_column_name(node.get_text(" ", strip=True))
               for node in header_nodes]
    headers = _make_unique_headers(headers)

    if not headers or any(not header for header in headers):
        logger.warning("Web scraping found invalid or missing headers")
        return pd.DataFrame()

    rows = table.select(row_selector)
    records: list[dict] = []

    for row in rows:
        cells = row.select(cell_selector)
        if len(cells) != len(headers):
            continue

        values = [cell.get_text(" ", strip=True) for cell in cells]
        if any(value for value in values):
            records.append(dict(zip(headers, values)))

    data = pd.DataFrame(records, columns=headers)

    if "student_id" in data.columns:
        data["student_id"] = pd.to_numeric(
            data["student_id"], errors="coerce"
        ).astype("Int64")
        data = data.dropna(subset=["student_id"])
        data = data.drop_duplicates(subset=["student_id"], keep="last")

    logger.info("Number of scraped records: %s", len(data))
    return data.reset_index(drop=True)


def _normalize_column_name(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def _make_unique_headers(headers: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    result: list[str] = []

    for header in headers:
        counts[header] = counts.get(header, 0) + 1
        result.append(
            header if counts[header] == 1 else f"{header}_{counts[header]}"
        )

    return result
