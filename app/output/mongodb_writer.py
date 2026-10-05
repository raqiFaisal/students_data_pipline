from __future__ import annotations

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger()


def load_to_mongodb(
    data: pd.DataFrame,
    url: str,
    database: str = "student_pipeline",
    collection: str = "final_students",
) -> dict[str, int]:
    """Upsert final records into MongoDB using student_id as the logical key."""
    if data.empty:
        logger.info("MongoDB loading skipped: no valid records")
        return {"inserted": 0, "updated": 0}

    try:
        from pymongo import MongoClient, ReplaceOne
        from pymongo.errors import DuplicateKeyError
    except ImportError as exc:
        raise RuntimeError(
            "MongoDB output requires pymongo. Install it with: "
            "pip install pymongo"
        ) from exc

    if "student_id" not in data.columns:
        raise ValueError("MongoDB loading requires student_id")

    documents = data.copy()
    documents = documents.drop_duplicates(subset=["student_id"], keep="last")
    records = documents.to_dict(orient="records")

    # Convert pandas NA values into MongoDB-safe None values.
    def _mongo_safe(value):
        if isinstance(value, list):
            return [_mongo_safe(item) for item in value]
        if isinstance(value, dict):
            return {key: _mongo_safe(item) for key, item in value.items()}
        return None if pd.isna(value) else value

    records = [
        {key: _mongo_safe(value) for key, value in record.items()}
        for record in records
    ]

    logger.info("MongoDB loading started: %s records", len(records))

    client = MongoClient(url, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        target = client[database][collection]
        target.create_index("student_id", unique=True, name="uq_student_id")

        operations = [
            ReplaceOne({"student_id": record["student_id"]}, record, upsert=True)
            for record in records
        ]

        result = target.bulk_write(operations, ordered=False)
        stats = {
            "inserted": result.upserted_count,
            "updated": result.modified_count,
        }
        logger.info(
            "MongoDB loading completed: inserted=%s updated=%s",
            stats["inserted"],
            stats["updated"],
        )
        return stats
    except DuplicateKeyError as exc:
        logger.error("MongoDB unique-key conflict: %s", exc)
        raise
    finally:
        client.close()
