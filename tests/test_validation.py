import pandas as pd

from app.validation.quality import validate_sources


def test_validate_sources():
    data = pd.DataFrame(
        {
            "student_id": [1001, 1002, None],
            "age": [20, 25, 30],
            "gpa": [3.5, 4.0, 3.2],
            "attendance": [90, 80, 85],
            "score": [95, 88, 92],
        }
    )

    valid_data, rejected_data = validate_sources(data)

    assert len(valid_data) == 2
    assert len(rejected_data) == 1

    assert "rejection_reason" in rejected_data.columns
    assert "Missing student_id" in rejected_data.iloc[0]["rejection_reason"]


def test_invalid_gpa_is_rejected():
    data = pd.DataFrame(
        {
            "student_id": [1001],
            "age": [20],
            "gpa": [5.0],
            "attendance": [90],
            "score": [95],
        }
    )

    valid_data, rejected_data = validate_sources(data)

    assert len(valid_data) == 0
    assert len(rejected_data) == 1
    assert "Invalid gpa" in rejected_data.iloc[0]["rejection_reason"]


def test_invalid_age_is_rejected():
    data = pd.DataFrame(
        {
            "student_id": [1001],
            "age": [10],
            "gpa": [3.5],
            "attendance": [90],
            "score": [95],
        }
    )

    valid_data, rejected_data = validate_sources(data)

    assert len(valid_data) == 0
    assert len(rejected_data) == 1
    assert "Invalid age" in rejected_data.iloc[0]["rejection_reason"]