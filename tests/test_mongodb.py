import pandas as pd

from app.output.mongodb_writer import load_to_mongodb
from app.sources.mongodb import extract_mongodb


def test_mongodb_source_is_optional():
    data = extract_mongodb("")
    assert data.empty


def test_mongodb_upsert_logic(monkeypatch):
    import app.output.mongodb_writer as writer

    class FakeResult:
        upserted_count = 1
        modified_count = 1

    class FakeCollection:
        def create_index(self, *args, **kwargs):
            return "uq_student_id"

        def bulk_write(self, operations, ordered=False):
            assert ordered is False
            assert len(operations) == 2
            return FakeResult()

    class FakeDatabase:
        def __getitem__(self, name):
            return FakeCollection()

    class FakeAdmin:
        def command(self, name):
            assert name == "ping"

    class FakeClient:
        admin = FakeAdmin()

        def __init__(self, *args, **kwargs):
            pass

        def __getitem__(self, name):
            return FakeDatabase()

        def close(self):
            pass

    monkeypatch.setattr(writer, "pd", pd)
    class DuplicateKeyError(Exception):
        pass

    pymongo_module = type("M", (), {
        "MongoClient": FakeClient,
        "ReplaceOne": lambda filt, doc, upsert=False: (filt, doc, upsert),
    })
    errors_module = type("E", (), {"DuplicateKeyError": DuplicateKeyError})
    import sys
    monkeypatch.setitem(sys.modules, "pymongo", pymongo_module)
    monkeypatch.setitem(sys.modules, "pymongo.errors", errors_module)

    data = pd.DataFrame({"student_id": [1001, 1002], "gpa": [3.5, 3.8]})
    result = load_to_mongodb(data, "mongodb://localhost:27017")
    assert result == {"inserted": 1, "updated": 1}
