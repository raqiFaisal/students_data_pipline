# Student Data Pipeline

## Overview

This project implements an ETL data pipeline that collects student data from multiple sources, integrates it using `student_id`, cleans and transforms the data, validates it, and loads the final valid records into MongoDB.

### Sources

- CSV
- REST API
- SQLite database
- Optional MongoDB source
- Web Scraping from an HTML page/table

### Final destination

- MongoDB database: `student_pipeline`
- Collection: `final_students`

The MongoDB writer uses a unique index on `student_id` and `upsert`, so rerunning the pipeline does not create duplicate documents.

## Pipeline

```text
CSV ───────────────┐
API ───────────────┤
SQLite ────────────┤
MongoDB (optional) ┤
Web Scraping ──────┘
        ↓
   Integration
        ↓
     Cleaning
        ↓
 Transformation
        ↓
    Validation
      ↙     ↘
 Valid      Rejected
   ↓           ↓
MongoDB     CSV file
   ↓
Final destination
```

## Web Scraping

The scraper is implemented in:

`app/sources/web_scraper.py`

It uses `requests` and `BeautifulSoup`, then returns a pandas `DataFrame`.

The URL and CSS selectors are configured in `config.json`:

```json
"scraping": {
    "enabled": true,
    "url": "http://localhost:8000/scraped-students",
    "timeout": 10,
    "selectors": {
        "table": "#students",
        "rows": "tbody tr",
        "headers": "thead th",
        "cells": "td"
    }
}
```

If the page cannot be reached or the configured table/elements are not found, the scraper logs the problem and returns an empty DataFrame instead of stopping the entire pipeline.

## Integration

All sources are joined using:

`student_id`

Each source is reduced to one record per `student_id` before merging. Pandas `merge(..., validate="one_to_one")` is used to prevent accidental Cartesian products or row multiplication.

## Cleaning and transformation

The existing cleaning/transformation modules are reused. They handle:

- Duplicate `student_id` records
- Missing values
- Text normalization
- Numeric type conversion
- Range checks
- Email/phone/skills cleaning
- Derived columns such as `performance_level` and `attendance_status`

## Validation

Required fields and value ranges are checked before loading.

Invalid records are separated into:

`data/rejected/rejected_records.csv`

Only valid records are sent to MongoDB.

## MongoDB

MongoDB configuration is stored in `config.json` rather than hard-coded in Python:

```json
"mongodb": {
    "enabled": true,
    "uri": "mongodb://localhost:27017",
    "database": "student_pipeline",
    "collection": "final_students"
}
```

The final loader:

1. Connects to MongoDB.
2. Verifies the connection with `ping`.
3. Creates a unique index on `student_id`.
4. Uses `ReplaceOne(..., upsert=True)` for each final record.
5. Reports inserted and updated counts in the log.

No `delete_many()` is used, so an existing collection is not wiped on every pipeline run.

## Configuration

All important source/output settings are in `config.json`.

Do not place passwords or secrets directly in source code. For a real deployment, use environment variables or a secret manager for credentials.

## Installation

From the project root:

```bash
pip install -r requirements.txt
```

## Running the local mock API

Open a terminal and run:

```bash
python mock_api/server.py
```

Keep it running while executing the pipeline.

## Running the pipeline

Make sure MongoDB is running locally, then from the project root:

```bash
python main.py
```

The pipeline will execute:

```text
Extract
  ↓
Integrate
  ↓
Clean
  ↓
Transform
  ↓
Validate
  ↓
Load valid data to MongoDB
```

It also writes rejected records to:

- `data/rejected/rejected_records.csv`
- `logs/pipeline.log`

The processed valid dataset is **not written to a final CSV**. MongoDB is the final destination:

- Database: `student_pipeline`
- Collection: `final_students`

## Tests

Run:

```bash
python -m pytest -q
```

The project includes tests for scraping, integration, validation, logging, pipeline outputs, and MongoDB upsert logic.

## Expected local setup

For the included mock data, the pipeline produces 15 final valid records with unique `student_id` values when all configured sources are available. The scraping source contributes columns such as `city_scraping` and `web_status` without replacing the existing CSV `city` column.

For the final MongoDB load to occur on your machine, MongoDB must be reachable at the configured URI and `pymongo` must be installed.
