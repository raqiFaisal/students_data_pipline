from __future__ import annotations

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger()


def extract_mongodb(
    url: str | None = None,
    database: str = "student_data",
    collection: str = "student_extra_data",
) -> pd.DataFrame:
    """Extract optional MongoDB source data without breaking the pipeline."""
    if not url:
        return pd.DataFrame()

    try:
        from pymongo import MongoClient
    except ImportError:
        logger.warning("pymongo is not installed; MongoDB source skipped")
        return pd.DataFrame()

    client = MongoClient(url, serverSelectionTimeoutMS=3000)
    try:
        client.admin.command("ping")
        data = list(client[database][collection].find({}, {"_id": 0}))
        result = pd.DataFrame(data)
        logger.info("MongoDB source records: %s", len(result))
        return result
    except Exception as exc:
        logger.warning("MongoDB source unavailable: %s", exc)
        return pd.DataFrame()
    finally:
        client.close()
