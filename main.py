import json
from pathlib import Path

from app.output.mongodb_writer import load_to_mongodb
from app.sources.api_source import extract_api
from app.sources.csv_source import extract_csv
from app.sources.database_source import extract_database
from app.sources.mongodb import extract_mongodb
from app.sources.web_scraper import extract_web_table
from app.transformation.cleaner import clean_data
from app.transformation.integration import integrate_data
from app.transformation.transformer import transform_data
from app.utils.logger import get_logger
from app.validation.quality import validate_sources


logger = get_logger()


def load_config() -> dict:
    """Load pipeline configuration from config.json."""
    config_path = Path("config.json")
    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    config = load_config()
    logger.info("Pipeline started")

    sources = config["sources"]
    output = config["output"]

    # 1. Extract
    logger.info("Extract stage started")

    csv_data = extract_csv(sources["csv"]["path"])
    logger.info("CSV records: %s", len(csv_data))

    api_cfg = sources.get("api", {})
    api_data = (
        extract_api(api_cfg.get("url", ""), api_cfg.get("timeout", 10))
        if api_cfg.get("enabled", True)
        else []
    )
    logger.info("API records: %s", len(api_data))

    database_cfg = sources.get("database", {})
    database_data = (
        extract_database(database_cfg["path"])
        if database_cfg.get("enabled", True)
        else []
    )
    logger.info("SQLite records: %s", len(database_data))

    mongo_source_cfg = sources.get("mongodb", {})
    mongo_data = (
        extract_mongodb(
            mongo_source_cfg.get("uri"),
            mongo_source_cfg.get("database", "student_data"),
            mongo_source_cfg.get("collection", "student_extra_data"),
        )
        if mongo_source_cfg.get("enabled", False)
        else None
    )
    logger.info("MongoDB source records: %s", len(mongo_data) if mongo_data is not None else 0)

    scraping_cfg = sources.get("scraping", {})
    scraping_data = None
    if scraping_cfg.get("enabled", False):
        selectors = scraping_cfg.get("selectors", {})
        scraping_data = extract_web_table(
            scraping_cfg.get("url", ""),
            table_selector=selectors.get("table", "table"),
            row_selector=selectors.get("rows", "tbody tr"),
            header_selector=selectors.get("headers", "th"),
            cell_selector=selectors.get("cells", "td"),
            timeout=scraping_cfg.get("timeout", 10),
        )
    else:
        scraping_data = None
        logger.info("Web scraping is disabled")

    logger.info("Extract stage completed")

    # 2. Integrate
    logger.info("Integration started")
    data = integrate_data(
        csv_data,
        api_data,
        database_data,
        mongo_data,
        scraping_data,
    )
    logger.info("Integration completed: %s records", len(data))

    # 3. Clean
    logger.info("Cleaning started: %s records before cleaning", len(data))
    before_cleaning = len(data)
    data = clean_data(data)
    logger.info(
        "Cleaning completed: %s -> %s records",
        before_cleaning,
        len(data),
    )

    # 4. Transform
    logger.info("Transformation started")
    data = transform_data(data)
    logger.info("Transformation completed: %s records", len(data))

    # 5. Validate and separate rejected records
    logger.info("Validation started")
    valid_data, rejected_data = validate_sources(data)
    logger.info(
        "Validation completed: valid=%s rejected=%s",
        len(valid_data),
        len(rejected_data),
    )

    rejected_path = Path(output["rejected"]["path"])
    rejected_path.parent.mkdir(parents=True, exist_ok=True)
    rejected_data.to_csv(rejected_path, index=False)

    # 6. Load final valid records to MongoDB
    mongo_output_cfg = output.get("mongodb", {})
    if mongo_output_cfg.get("enabled", False):
        logger.info("MongoDB loading started")
        stats = load_to_mongodb(
            valid_data,
            mongo_output_cfg["uri"],
            mongo_output_cfg.get("database", "student_pipeline"),
            mongo_output_cfg.get("collection", "final_students"),
        )
        logger.info(
            "MongoDB loading completed: inserted=%s updated=%s",
            stats["inserted"],
            stats["updated"],
        )
    else:
        logger.warning("MongoDB final destination is disabled")

    logger.info("Pipeline completed successfully")
    print("Pipeline completed successfully!")
    print(f"Final valid records loaded to MongoDB: {len(valid_data)}")
    print(f"Rejected records: {len(rejected_data)}")
    print(
        "MongoDB destination: "
        f"{mongo_output_cfg.get('database', 'student_pipeline')}."
        f"{mongo_output_cfg.get('collection', 'final_students')}"
    )


if __name__ == "__main__":
    main()
