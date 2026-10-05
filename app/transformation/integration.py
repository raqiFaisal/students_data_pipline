from __future__ import annotations

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger()


def _to_source_frame(source: pd.DataFrame | list[dict] | None) -> pd.DataFrame:
    if isinstance(source, pd.DataFrame):
        return source.copy()
    return pd.DataFrame(source or [])


def _prepare_source(source: pd.DataFrame, source_name: str) -> pd.DataFrame:
    if source.empty:
        return source

    if "student_id" not in source.columns:
        raise ValueError(f"{source_name} source must contain 'student_id'")

    source["student_id"] = pd.to_numeric(source["student_id"], errors="coerce")
    source = source.dropna(subset=["student_id"]).copy()
    source["student_id"] = source["student_id"].astype("Int64")

    before = len(source)
    source = source.drop_duplicates(subset=["student_id"], keep="last")
    logger.info(
        "%s integration preparation: %s -> %s records",
        source_name,
        before,
        len(source),
    )
    return source


def integrate_data(
    csv_data: pd.DataFrame,
    api_data: list[dict],
    database_data: list[dict],
    mongo_data: pd.DataFrame | list[dict] | None = None,
    scraping_data: pd.DataFrame | list[dict] | None = None,
) -> pd.DataFrame:
    """Integrate all sources on student_id without row multiplication."""
    if csv_data.empty:
        return pd.DataFrame()

    integrated_df = csv_data.copy()
    integrated_df["student_id"] = pd.to_numeric(
        integrated_df["student_id"], errors="coerce"
    ).astype("Int64")
    integrated_df = integrated_df.dropna(subset=["student_id"])
    integrated_df = integrated_df.drop_duplicates(subset=["student_id"], keep="last")

    sources = [
        ("API", _to_source_frame(api_data)),
        ("SQLite", _to_source_frame(database_data)),
        ("MongoDB", _to_source_frame(mongo_data)),
        ("Scraping", _to_source_frame(scraping_data)),
    ]

    for source_name, source_df in sources:
        if source_df.empty:
            continue

        source_df = _prepare_source(source_df, source_name)
        overlapping_columns = (
            set(integrated_df.columns) & set(source_df.columns)
        ) - {"student_id"}

        if overlapping_columns:
            source_df = source_df.rename(
                columns={
                    column: f"{column}_{source_name.lower()}"
                    for column in overlapping_columns
                }
            )

        before = len(integrated_df)
        integrated_df = integrated_df.merge(
            source_df,
            on="student_id",
            how="left",
            validate="one_to_one",
        )

        if len(integrated_df) != before:
            raise ValueError(
                f"{source_name} integration changed row count from "
                f"{before} to {len(integrated_df)}"
            )

    logger.info("Integration completed: %s records", len(integrated_df))
    return integrated_df.reset_index(drop=True)
