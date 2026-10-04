import pytest
from bson import ObjectId

from helpers.id_helpers import is_valid_id, parse_id


@pytest.mark.unit
class TestParseId:
    def test_parses_object_id(self):
        oid = ObjectId()
        assert parse_id(str(oid)) == oid

    def test_parses_numeric_id(self):
        assert parse_id("123456") == 123456

    def test_rejects_invalid_id(self):
        with pytest.raises(RuntimeError, match="Id must be of type int or ObjectId"):
            parse_id("not-an-id")


@pytest.mark.unit
class TestIsValidId:
    def test_accepts_object_id_and_digits(self):
        assert is_valid_id(str(ObjectId()))
        assert is_valid_id("42")

    def test_rejects_other_strings(self):
        assert not is_valid_id("abc")
        assert not is_valid_id("")
