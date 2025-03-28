from typing import Optional
from pydantic import ValidationError
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import PyMongoError
import logging

from src.models import BitcoinAddressQueryResponse, Transaction

API_CACHE_DB = "api_cache"
ADDRESS_COLLECTION = "addresses"
METADATA_COLLECTION = "metadata"

ADDRESS_NEVER_PROCESSED = -1


logger = logging.getLogger(__name__)


def set_up_database(mongo_client: MongoClient) -> None:
    """
    Set up the database for the API cache.

    Parameters:
    - mongo_client: The MongoDB client instance
    """
    # Create the database if it doesn't exist
    db = mongo_client[API_CACHE_DB]

    # Create the metadata collection if it doesn't exist
    metadata = db[METADATA_COLLECTION]

    # Ensure the metadata collection has a document for the last processed block height
    if metadata.count_documents({"_id": "last_processed_block_height"}) == 0:
        metadata.insert_one({"_id": "last_processed_block_height", "height": 0})


def set_address_last_processed_block_height(
    mongo_client: MongoClient, address: str, height: int
) -> None:
    """
    Set the last processed block height for a specific address in the database.

    Parameters:
    - mongo_client: The MongoDB client instance
    - address: Bitcoin address
    - height: The block height to set
    """
    db = mongo_client[API_CACHE_DB]
    addresses = db[ADDRESS_COLLECTION]
    addresses.update_one(
        {"_id": address},
        {"$set": {"last_processed_height": height}},
        upsert=True,
    )


def get_address_last_processed_block_height(
    mongo_client: MongoClient, address: str
) -> int:
    """
    Get the last processed block height for a specific address from the database.

    Parameters:
    - mongo_client: The MongoDB client instance
    - address: Bitcoin address

    Returns:
    - The last processed block height for the address, or ADDRESS_NEVER_PROCESSED if not found
    """
    db = mongo_client[API_CACHE_DB]
    addresses = db[ADDRESS_COLLECTION]
    document = addresses.find_one({"_id": address})
    if document and "last_processed_height" in document:
        return document["last_processed_height"]
    else:
        return ADDRESS_NEVER_PROCESSED


def get_last_processed_block_height(mongo_client: MongoClient) -> int:
    """
    Get the last processed block height from the database.

    Parameters:
    - mongo_client: The MongoDB client instance

    Returns:
    - The last processed block height
    """
    db = mongo_client[API_CACHE_DB]
    metadata = db[METADATA_COLLECTION]
    document = metadata.find_one({"_id": "last_processed_block_height"})
    if document:
        return document["height"]
    else:
        return 0


def set_last_processed_block_height(mongo_client: MongoClient, height: int) -> None:
    """
    Set the last processed block height in the database.

    Parameters:
    - mongo_client: The MongoDB client instance
    - height: The block height to set
    """
    db = mongo_client[API_CACHE_DB]
    metadata = db[METADATA_COLLECTION]
    metadata.update_one(
        {"_id": "last_processed_block_height"},
        {"$set": {"height": height}},
        upsert=True,
    )
