from pymongo import MongoClient
import os

db = None

def connect():
    try:
        CONNECTION_STRING = os.environ['MONGO_ID']

        client = MongoClient(CONNECTION_STRING)

        global db
        db = client[os.environ['DBNAME']]

        print('Connected to MongoDB')
    except:
        raise RuntimeError('Could not connect to MongoDB')

def insert_to_collection(collectionName, data):
    try:
        collection = db[collectionName]

        collection.insert_one(data)
    except:
        raise RuntimeError(f"Failed to insert into collection '{collectionName}'")

# returns all data in a particular collection
def get_collection(collectionName):
    try:
        collection = db[collectionName]
        data = collection.find()

        return data
    except:
        print(f"Failed while fetching data from '{collectionName}'")

    return None

# returns a singular item in a collection, by id
def find_in_collection(collectionName, id):
    try:
        collection = db[collectionName]
        data = collection.find({'_id': id})

        # data should only contain one element due to its unique id
        for item in data:
            if item['_id'] == id:
                return item
    except:
        print(f"Failed while fetching single query from '{collectionName}'")

    return None

def update_collection(collectionName, id, data):
    try:
        collection = db[collectionName]

        collection.update_one({'_id': id}, {"$set": data}, upsert=True)
    except:
        raise RuntimeError(f"Failed to update the collection '{collectionName}'")