from pathlib import Path

from app.utils.logger import get_logger


def test_logger_creates_log_file():
    logger = get_logger("test_logger")

    logger.info("Test log message")

    log_file = Path("logs/pipeline.log")

    assert log_file.exists()
    assert "Test log message" in log_file.read_text(encoding="utf-8")