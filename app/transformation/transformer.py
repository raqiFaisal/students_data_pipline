import pandas as pd


def normalize_column_names(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to lowercase snake_case."""
    transformed = data.copy()

    transformed.columns = (
        transformed.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return transformed

def transform_skills(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize skills data from MongoDB."""
    transformed = data.copy()

    if "skills" in transformed.columns:
        transformed["skills"] = transformed["skills"].apply(
            lambda skills: skills if isinstance(skills, list) else []
        )

    return transformed


def convert_data_types(data: pd.DataFrame) -> pd.DataFrame:
    """Convert columns to appropriate data types."""
    transformed = data.copy()

    integer_columns = ["student_id", "credit_hours"]

    for column in integer_columns:
        if column in transformed.columns:
            transformed[column] = pd.to_numeric(
                transformed[column],
                errors="coerce",
            ).astype("Int64")

    float_columns = ["age", "gpa", "attendance", "score"]

    for column in float_columns:
        if column in transformed.columns:
            transformed[column] = pd.to_numeric(
                transformed[column],
                errors="coerce",
            )

    # MongoDB fields
    if "email" in transformed.columns:
        transformed["email"] = transformed["email"].astype("string")

    if "phone" in transformed.columns:
        transformed["phone"] = transformed["phone"].astype("string")

    return transformed

def create_derived_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Create derived columns required for analysis."""
    transformed = data.copy()

    if "gpa" in transformed.columns:
        transformed["performance_level"] = pd.cut(
            transformed["gpa"],
            bins=[-float("inf"), 2.0, 2.5, 3.0, 3.5, float("inf")],
            labels=[
                "At Risk",
                "Acceptable",
                "Good",
                "Very Good",
                "Excellent",
            ],
        )

    if "attendance" in transformed.columns:
        transformed["attendance_status"] = transformed["attendance"].apply(
            lambda value: "Good" if value >= 75 else "Low"
        )

    return transformed


def transform_data(data: pd.DataFrame) -> pd.DataFrame:
    """Run all transformation steps."""
    transformed = normalize_column_names(data)
    transformed = convert_data_types(transformed)
    transformed = transform_skills(transformed)
    transformed = create_derived_columns(transformed)

    return transformed