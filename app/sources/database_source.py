import sqlite3
from pathlib import Path


def extract_database(db_path: str | Path) -> list[dict]:
    """Extract enrollment data with course details from SQLite."""
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    try:
        query = """
            SELECT
                e.student_id,
                e.course_id,
                c.course_name,
                c.credit_hours,
                e.semester,
                e.score
            FROM enrollments AS e
            JOIN courses AS c
                ON e.course_id = c.course_id
        """

        rows = connection.execute(query).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()