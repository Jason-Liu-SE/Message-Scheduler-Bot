import pymongo
from pymongo import MongoClient
import os
from datetime import datetime

db = None


def connect():
    try:
        CONNECTION_STRING = os.environ["MONGO_ID"]

        client = MongoClient(CONNECTION_STRING)

        global db
        db = client[os.environ["DBNAME"]]

        print("Connected to MongoDB")
    except:
        raise RuntimeError("ERROR: Could not connect to MongoDB")


def insert_to_collection(collectionName, data):
    try:
        collection = db[collectionName]

        collection.insert_one(data)
    except:
        raise RuntimeError(
            f"ERROR: Failed to insert into collection '{collectionName}'"
        )


# returns a  item in a collection, by id
def find_in_collection_by_id(collectionName, id):
    try:
        collection = db[collectionName]
        data = collection.find_one({"_id": id})

        return data
    except:
        print(f"ERROR: Failed while fetching single query from '{collectionName}'")

    return None


def find_all_in_collection(collectionName, query):
    try:
        collection = db[collectionName]
        rawData = collection.find(query)

        data = {}

        for item in rawData:
            temp = item
            itemId = temp["_id"]
            del temp["_id"]

            data[itemId] = temp

        return data
    except:
        print(
            f"ERROR: Failed while fetching all from '{collectionName}' with query '{query}'"
        )


def update_collection(collectionName, id, data):
    try:
        collection = db[collectionName]

        collection.update_one({"_id": id}, {"$set": data}, upsert=True)
    except:
        raise RuntimeError(f"ERROR: Failed to update the collection '{collectionName}'")


def get_posts_in_date_range(start, end):
    try:
        collection = db["schedules"]

        rawData = collection.find({"time": {"$gte": start, "$lte": end}})
        rawData.sort([("server_id", pymongo.ASCENDING), ("channel", pymongo.ASCENDING)])

        data = []

        if rawData:
            for item in rawData:
                data.append(item)

        return data
    except:
        raise RuntimeError(
            f"ERROR: Failed to retrieve entries in collection 'schedules' for date range {start} to {end}"
        )


def delete_by_id(collection, id):
    try:
        collection = db[collection]

        collection.delete_one({"_id": id})
    except:
        raise RuntimeError(
            f"ERROR: Failed to delete entry in collection '{collection}' with id '{id}'"
        )


def delete_all_by_query(collection, query):
    try:
        collection = db[collection]

        collection.delete_many(query)
    except:
        raise RuntimeError(
            f"ERROR: Failed to delete entries in collection '{collection}' with query '{query}'"
        )
