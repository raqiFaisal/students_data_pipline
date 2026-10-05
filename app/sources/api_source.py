import pandas as pd
import requests

from app.utils.logger import get_logger

logger = get_logger()


def extract_api(url: str, timeout: int = 10) -> list[dict]:
    """Extract API records without stopping the pipeline on source failure."""
    if not url:
        logger.warning("API extraction skipped: URL is empty")
        return []

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.error("API extraction failed: %s", exc)
        return []

    if not data:
        return []
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data

    logger.error("Invalid API response format")
    return []
