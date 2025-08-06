from datetime import datetime
from typing import Literal
from bson import ObjectId
from helpers.logger import Logger
from pymongo import MongoClient
import os


class PymongoManager:
    __db = None

    @staticmethod
    def connect() -> None:
        try:
            CONNECTION_STRING = os.environ["MONGO_ID"]

            client = MongoClient(CONNECTION_STRING)

            PymongoManager.__db = client[os.environ["DBNAME"]]

            Logger.info("Connected to MongoDB")
        except:
            raise RuntimeError("Could not connect to MongoDB")

    @staticmethod
    def insert_to_collection(collectionName: str, data: dict) -> None:
        try:
            collection = PymongoManager.__db[collectionName]

            collection.insert_one(data)
        except:
            raise RuntimeError(f"Failed to insert into collection '{collectionName}'")

    # returns an item in a collection, by id
    @staticmethod
    def find_in_collection_by_id(collectionName: str, id: int | ObjectId) -> dict:
        try:
            collection = PymongoManager.__db[collectionName]
            data = collection.find_one({"_id": id})

            return data
        except:
            Logger.error(f"Failed while fetching single query from '{collectionName}'")

        return {}

    @staticmethod
    def find_many_in_collection(
        collectionName: str,
        query: dict,
        sort: str = None,
        dir: Literal["ASC", "DESC"] = "ASC",
        limit: int = 0,
    ) -> dict:
        try:
            collection = PymongoManager.__db[collectionName]
            rawData = collection.find(query).limit(limit)

            if sort:
                rawData = rawData.sort(sort, 1 if dir == "ASC" else -1)

            data = {}

            for item in rawData:
                temp = item
                itemId = temp["_id"]
                del temp["_id"]

                data[itemId] = temp

            return data
        except:
            Logger.error(
                f"Failed while fetching all from '{collectionName}' with query '{query}'"
            )

        return {}

    @staticmethod
    def update_collection(collectionName: str, id: int | ObjectId, data: dict) -> None:
        try:
            collection = PymongoManager.__db[collectionName]

            collection.update_one({"_id": id}, {"$set": data}, upsert=True)
        except:
            raise RuntimeError(f"Failed to update the collection '{collectionName}'")

    @staticmethod
    def update_collection_on_insert(
        collectionName: str, id: int | ObjectId, data: dict
    ) -> None:
        try:
            collection = PymongoManager.__db[collectionName]

            collection.update_one({"_id": id}, {"$setOnInsert": data}, upsert=True)
        except:
            raise RuntimeError(
                f"Failed to set on insert for collection: '{collectionName}'"
            )

    @staticmethod
    def delete_by_id(collectionName: str, id: int | ObjectId) -> None:
        try:
            collection = PymongoManager.__db[collectionName]

            collection.delete_one({"_id": id})
        except:
            raise RuntimeError(
                f"Failed to delete entry in collection '{collectionName}' with id '{id}'"
            )

    @staticmethod
    def delete_all_by_query(collectionName: str, query: dict) -> None:
        try:
            collection = PymongoManager.__db[collectionName]

            collection.delete_many(query)
        except:
            raise RuntimeError(
                f"Failed to delete entries in collection '{collectionName}' with query '{query}'"
            )

    @staticmethod
    def find_in_range(
        collectionName: str,
        field: str,
        start: datetime,
        end: datetime,
        sort: str = None,
        dir: Literal["ASC", "DESC"] = "ASC",
    ) -> list:
        try:
            collection = PymongoManager.__db[collectionName]

            rawData = collection.find({field: {"$gte": start, "$lte": end}})

            if sort:
                rawData = rawData.sort(sort, 1 if dir == "ASC" else -1)

            data = []

            if rawData:
                for item in rawData:
                    data.append(item)

            return data
        except:
            raise RuntimeError(
                f"Failed to retrieve entries in collection '{collectionName}' for date range {start} to {end}"
            )
