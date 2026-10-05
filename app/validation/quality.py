from __future__ import annotations

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger()


def validate_sources(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Validate records and separate valid rows from rejected rows."""
    validated = data.copy()
    rejected = []
    rejected_indices = []

    required_columns = ["student_id", "age", "gpa", "attendance", "score"]
    for column in required_columns:
        if column not in validated.columns:
            raise ValueError(f"Missing required column: {column}")

    for index, row in validated.iterrows():
        reasons = []
        if pd.isna(row["student_id"]):
            reasons.append("Missing student_id")
        if pd.isna(row["age"]) or not 16 <= row["age"] <= 80:
            reasons.append("Invalid age")
        if pd.isna(row["gpa"]) or not 0 <= row["gpa"] <= 4:
            reasons.append("Invalid gpa")
        if pd.isna(row["attendance"]) or not 0 <= row["attendance"] <= 100:
            reasons.append("Invalid attendance")
        if pd.isna(row["score"]) or not 0 <= row["score"] <= 100:
            reasons.append("Invalid score")

        if reasons:
            rejected_row = row.to_dict()
            rejected_row["rejection_reason"] = "; ".join(reasons)
            rejected.append(rejected_row)
            rejected_indices.append(index)

    rejected_df = pd.DataFrame(rejected)
    valid_data = validated.drop(index=rejected_indices).copy()
    valid_data = valid_data.drop_duplicates(subset=["student_id"], keep="first")

    logger.info(
        "Validation completed: valid=%s rejected=%s",
        len(valid_data),
        len(rejected_df),
    )
    return valid_data, rejected_df


def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    """Backward-compatible validation entry point used by the pipeline."""
    valid_data, _ = validate_sources(data)
    return valid_data
