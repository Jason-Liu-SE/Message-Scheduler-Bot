from datetime import datetime, timedelta

import pytest
from bson import ObjectId

from managers.pymongo_manager import PymongoManager


@pytest.mark.unit
class TestPymongoManager:
    def test_insert_find_update_and_delete(self, fake_db):
        oid = ObjectId()
        PymongoManager.insert_to_collection(
            "tickets", {"_id": oid, "tickets": 3, "name": "A"}
        )
        found = PymongoManager.find_in_collection_by_id("tickets", oid)
        assert found["tickets"] == 3

        PymongoManager.update_collection("tickets", oid, {"tickets": 8})
        assert PymongoManager.find_in_collection_by_id("tickets", oid)["tickets"] == 8

        PymongoManager.delete_by_id("tickets", oid)
        assert PymongoManager.find_in_collection_by_id("tickets", oid) is None

    def test_find_many_strips_id_and_uses_it_as_key(self, fake_db):
        fake_db.seed(
            "tickets",
            [
                {"_id": 1, "tickets": 5},
                {"_id": 2, "tickets": 9},
            ],
        )
        result = PymongoManager.find_many_in_collection(
            "tickets", {"_id": {"$in": [1, 2]}}, sort="tickets", dir="DESC"
        )
        assert list(result.keys()) == [2, 1]
        assert "_id" not in result[2]
        assert result[2]["tickets"] == 9

    def test_count_and_range_query(self, fake_db):
        start = datetime(2026, 1, 1)
        fake_db.seed(
            "schedules",
            [
                {"_id": 1, "time": start, "server_id": 10},
                {"_id": 2, "time": start + timedelta(days=1), "server_id": 10},
                {"_id": 3, "time": start + timedelta(days=2), "server_id": 10},
                {"_id": 4, "time": start + timedelta(days=3), "server_id": 10},
            ],
        )
        assert PymongoManager.count_in_collection("schedules", {"server_id": 10}) == 4
        in_range = PymongoManager.find_in_range(
            "schedules", "time", start, start + timedelta(days=2)
        )
        assert len(in_range) == 3
        assert in_range[0]["_id"] == 1

    def test_update_on_insert_does_not_overwrite(self, fake_db):
        PymongoManager.update_collection_on_insert(
            "tickets", 7, {"tickets": 0, "incoming_trades": []}
        )
        PymongoManager.update_collection("tickets", 7, {"tickets": 4})
        PymongoManager.update_collection_on_insert(
            "tickets", 7, {"tickets": 0, "incoming_trades": []}
        )
        assert PymongoManager.find_in_collection_by_id("tickets", 7)["tickets"] == 4

    def test_delete_all_by_query(self, fake_db):
        fake_db.seed(
            "schedules",
            [
                {"_id": 1, "server_id": 10},
                {"_id": 2, "server_id": 11},
                {"_id": 3, "server_id": 10},
            ],
        )
        PymongoManager.delete_all_by_query("schedules", {"server_id": 10})
        remaining = PymongoManager.find_many_in_collection("schedules", {})
        assert list(remaining.keys()) == [2]
