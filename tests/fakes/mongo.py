from copy import deepcopy
from bson import ObjectId
import re


def _matches(doc: dict, query: dict) -> bool:
    for key, value in query.items():
        field = doc.get(key)
        if isinstance(value, dict):
            if "$in" in value and field not in value["$in"]:
                return False
            if "$gte" in value and (field is None or field < value["$gte"]):
                return False
            if "$lte" in value and (field is None or field > value["$lte"]):
                return False
            if "$regex" in value:
                flags = re.IGNORECASE if "i" in value.get("$options", "") else 0
                if not re.search(value["$regex"], str(field), flags):
                    return False
        elif field != value:
            return False
    return True


class FakeCursor:
    def __init__(self, docs: list[dict]):
        self._docs = [deepcopy(doc) for doc in docs]

    def skip(self, n: int):
        self._docs = self._docs[n:]
        return self

    def limit(self, n: int):
        if n:
            self._docs = self._docs[:n]
        return self

    def sort(self, field: str, direction: int):
        reverse = direction == -1
        self._docs.sort(key=lambda doc: doc.get(field), reverse=reverse)
        return self

    def __iter__(self):
        return iter(deepcopy(self._docs))


class FakeCollection:
    def __init__(self):
        self.docs: dict = {}

    def insert_one(self, data: dict) -> None:
        stored = deepcopy(data)
        if "_id" not in stored:
            stored["_id"] = ObjectId()
        self.docs[stored["_id"]] = stored

    def find_one(self, query: dict) -> dict | None:
        if set(query.keys()) == {"_id"}:
            doc = self.docs.get(query["_id"])
            return deepcopy(doc) if doc else None

        for doc in self.docs.values():
            if _matches(doc, query):
                return deepcopy(doc)
        return None

    def find(self, query: dict):
        return FakeCursor([doc for doc in self.docs.values() if _matches(doc, query)])

    def count_documents(self, query: dict) -> int:
        return sum(1 for doc in self.docs.values() if _matches(doc, query))

    def update_one(self, query: dict, update: dict, upsert: bool = False) -> None:
        existing = self.find_one(query)
        if existing is None:
            if not upsert:
                return
            doc_id = query.get("_id", ObjectId())
            doc = {"_id": doc_id}
            if "$setOnInsert" in update:
                doc.update(deepcopy(update["$setOnInsert"]))
            if "$set" in update:
                doc.update(deepcopy(update["$set"]))
            self.docs[doc_id] = doc
            return

        doc_id = existing["_id"]
        if "$set" in update:
            self.docs[doc_id].update(deepcopy(update["$set"]))

    def delete_one(self, query: dict) -> None:
        if "_id" in query and query["_id"] in self.docs:
            del self.docs[query["_id"]]
            return
        for doc_id, doc in list(self.docs.items()):
            if _matches(doc, query):
                del self.docs[doc_id]
                return

    def delete_many(self, query: dict) -> None:
        for doc_id, doc in list(self.docs.items()):
            if _matches(doc, query):
                del self.docs[doc_id]


class FakeDB:
    def __init__(self):
        self._collections: dict[str, FakeCollection] = {}

    def __getitem__(self, name: str) -> FakeCollection:
        if name not in self._collections:
            self._collections[name] = FakeCollection()
        return self._collections[name]

    def seed(self, collection: str, documents: list[dict]) -> None:
        for document in documents:
            stored = deepcopy(document)
            if "_id" not in stored:
                stored["_id"] = ObjectId()
            self[collection].docs[stored["_id"]] = stored
