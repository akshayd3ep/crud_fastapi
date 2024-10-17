from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "wwe")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

sync_client = MongoClient(MONGODB_URL)


def get_collection(collection_name):
    return database[collection_name]


def object_id_to_str(obj_id):
    return str(obj_id)


def is_valid_object_id(id_str):
    return ObjectId.is_valid(id_str)


async def insert_many(payload, collection_name):
    collection = get_collection(collection_name)
    result = await collection.insert_many(payload)
    return [object_id_to_str(id) for id in result.inserted_ids]


async def insert_one(payload, collection_name):
    collection = get_collection(collection_name)
    result = await collection.insert_one(payload)
    return object_id_to_str(result.inserted_id)


async def update(filter_criteria, payload, collection_name):
    collection = get_collection(collection_name)
    result = await collection.update_many(filter_criteria, {"$set": payload})
    return {"matched_count": result.matched_count, "modified_count": result.modified_count}


async def delete(filter_criteria, collection_name):
    collection = get_collection(collection_name)
    result = await collection.delete_many(filter_criteria)
    return {"deleted_count": result.deleted_count}

async def find_one(filter_criteria, collection_name):
    collection = get_collection(collection_name)
    document = await collection.find_one(filter_criteria)
    if document:
        document['_id'] = object_id_to_str(document['_id'])  
    return document



async def find_all(filter_criteria, collection_name):
    collection = get_collection(collection_name)
    cursor = collection.find(filter_criteria)
    documents = []
    async for document in cursor:
        document["_id"] = object_id_to_str(document["_id"]) 
        documents.append(document)
    return documents

async def aggregate(pipeline, collection_name):
    collection = get_collection(collection_name)
    cursor = collection.aggregate(pipeline)
    results = []
    async for document in cursor:
        if "_id" in document and isinstance(document["_id"], ObjectId):
            document["_id"] = object_id_to_str(document["_id"])
        results.append(document)
    return results