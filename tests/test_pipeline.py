from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_csv_exists_and_has_data():
    path = PROJECT_ROOT / "data" / "raw" / "students.csv"

    assert path.exists()

    data = pd.read_csv(path)

    assert not data.empty
    assert "student_id" in data.columns


def test_api_output_exists():
    path = PROJECT_ROOT / "mock_api" / "server.py"

    assert path.exists()


def test_database_exists():
    path = PROJECT_ROOT / "database" / "students.db"

    assert path.exists()


def test_final_destination_is_mongodb():
    import json

    config = json.loads((PROJECT_ROOT / "config.json").read_text(encoding="utf-8"))
    output = config["output"]

    assert "csv" not in output
    assert output["mongodb"]["enabled"] is True
    assert output["mongodb"]["database"] == "student_pipeline"
    assert output["mongodb"]["collection"] == "final_students"


def test_rejected_records_file_path_is_configured():
    import json

    config = json.loads((PROJECT_ROOT / "config.json").read_text(encoding="utf-8"))
    assert config["output"]["rejected"]["path"] == "data/rejected/rejected_records.csv"


def test_integration_adds_source_columns():
    from app.transformation.integration import integrate_data

    csv_data = pd.DataFrame(
        {
            "student_id": [1001, 1002],
            "name": ["Ali", "Sara"],
        }
    )

    api_data = [
        {"student_id": 1001, "gpa": 3.5},
        {"student_id": 1002, "gpa": 3.8},
    ]

    database_data = [
        {"student_id": 1001, "course_id": "C101"},
        {"student_id": 1002, "course_id": "C102"},
    ]

    result = integrate_data(
        csv_data,
        api_data,
        database_data,
    )

    assert len(result) == 2
    assert "gpa" in result.columns
    assert "course_id" in result.columns

