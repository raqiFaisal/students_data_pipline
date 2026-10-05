import pandas as pd

from app.transformation.integration import integrate_data


def test_integrate_data():
    csv_data = pd.DataFrame(
        {"student_id": [1001, 1002], "name": ["Ali", "Sara"]}
    )
    api_data = [
        {"student_id": 1001, "gpa": 3.5},
        {"student_id": 1002, "gpa": 3.8},
    ]
    database_data = [
        {"student_id": 1001, "course_id": "C101"},
        {"student_id": 1002, "course_id": "C102"},
    ]
    scraping_data = pd.DataFrame(
        {"student_id": [1001, 1002], "web_status": ["Verified", "Review"]}
    )

    result = integrate_data(
        csv_data, api_data, database_data, scraping_data=scraping_data
    )

    assert len(result) == 2
    assert result["student_id"].is_unique
    assert "gpa" in result.columns
    assert "course_id" in result.columns
    assert "web_status" in result.columns
