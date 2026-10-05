import re

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger()


def clean_text_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Clean text columns by removing extra spaces and normalizing case."""
    cleaned = data.copy()

    text_columns = ["student_name", "major", "city", "status"]

    for column in text_columns:
        if column in cleaned.columns:
            cleaned[column] = (
                cleaned[column]
                .astype("string")
                .str.strip()
                .str.title()
            )

    return cleaned


def remove_duplicates(data: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate records based on student_id."""
    cleaned = data.copy()

    if "student_id" in cleaned.columns:
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates(subset=["student_id"])
        logger.info("Number of duplicates removed: %s", before - len(cleaned))

    return cleaned


def clean_invalid_values(data: pd.DataFrame) -> pd.DataFrame:
    """Replace invalid numeric values with missing values."""
    cleaned = data.copy()

    if "age" in cleaned.columns:
        cleaned.loc[
            ~cleaned["age"].between(16, 80, inclusive="both"),
            "age",
        ] = pd.NA

    if "gpa" in cleaned.columns:
        cleaned.loc[
            ~cleaned["gpa"].between(0, 4, inclusive="both"),
            "gpa",
        ] = pd.NA

    if "attendance" in cleaned.columns:
        cleaned.loc[
            ~cleaned["attendance"].between(0, 100, inclusive="both"),
            "attendance",
        ] = pd.NA

    if "score" in cleaned.columns:
        cleaned.loc[
            ~cleaned["score"].between(0, 100, inclusive="both"),
            "score",
        ] = pd.NA

    return cleaned


def clean_email(data: pd.DataFrame) -> pd.DataFrame:
    """Validate email addresses and replace invalid values with missing."""
    cleaned = data.copy()

    if "email" not in cleaned.columns:
        return cleaned

    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    def validate_email(value):
        if pd.isna(value) or str(value).strip() == "":
            return pd.NA

        value = str(value).strip().lower()

        if re.match(pattern, value):
            return value

        return pd.NA

    cleaned["email"] = cleaned["email"].apply(validate_email)

    return cleaned


def clean_phone(data: pd.DataFrame) -> pd.DataFrame:
    """Validate phone numbers and replace invalid values with missing."""
    cleaned = data.copy()

    if "phone" not in cleaned.columns:
        return cleaned

    def validate_phone(value):
        if pd.isna(value):
            return pd.NA

        value = str(value).strip()

        if value.isdigit() and 9 <= len(value) <= 10:
            return value

        return pd.NA

    cleaned["phone"] = cleaned["phone"].apply(validate_phone)

    return cleaned


def clean_skills(data: pd.DataFrame) -> pd.DataFrame:
    """Clean skills lists by handling missing values and duplicates."""
    cleaned = data.copy()

    if "skills" not in cleaned.columns:
        return cleaned

    def normalize_skills(value):
        if not isinstance(value, list):
            return []

        skills = []

        for skill in value:
            if pd.notna(skill):
                skill = str(skill).strip()

                if skill and skill not in skills:
                    skills.append(skill)

        return skills

    cleaned["skills"] = cleaned["skills"].apply(normalize_skills)

    return cleaned


def handle_missing_values(data: pd.DataFrame) -> pd.DataFrame:
    """Handle missing numeric and text values."""
    cleaned = data.copy()

    numeric_columns = ["age", "gpa", "attendance", "score"]

    for column in numeric_columns:
        if column in cleaned.columns:
            median = cleaned[column].median()
            cleaned[column] = cleaned[column].fillna(median)

    if "student_name" in cleaned.columns:
        cleaned["student_name"] = cleaned["student_name"].fillna("Unknown")

    return cleaned


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Run all data-cleaning steps."""
    cleaned = clean_text_columns(data)
    cleaned = remove_duplicates(cleaned)
    cleaned = clean_invalid_values(cleaned)

    # MongoDB fields
    cleaned = clean_email(cleaned)
    cleaned = clean_phone(cleaned)
    cleaned = clean_skills(cleaned)

    cleaned = handle_missing_values(cleaned)

    return cleaned