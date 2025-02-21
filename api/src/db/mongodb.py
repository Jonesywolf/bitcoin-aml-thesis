from typing import Optional
from pydantic import ValidationError
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import PyMongoError
import logging

from src.models import BitcoinAddressQueryResponse, Transaction

API_CACHE_DB = "api_cache"
ADDRESS_COLLECTION = "addresses"
TRANSACTION_COLLECTION = "transactions"
METADATA_COLLECTION = "metadata"


logger = logging.getLogger(__name__)


def set_up_database(mongo_client: MongoClient) -> None:
    """
    Set up the database for the API cache.

    Parameters:
    - mongo_client: The MongoDB client instance
    """
    # Create the database if it doesn't exist
    db = mongo_client[API_CACHE_DB]

    # Create the collections if they don't exist
    addresses = db[ADDRESS_COLLECTION]
    transactions = db[TRANSACTION_COLLECTION]
    metadata = db[METADATA_COLLECTION]

    # Add an index on 'address' in the addresses collection for efficient querying
    addresses.create_index("address", unique=True)

    # Add a compound index on the transactions collection for uniqueness of the address and transaction hash
    transactions.create_index(
        [("address", ASCENDING), ("txid", ASCENDING)], unique=True
    )

    # Add a compound index on the transactions collection for efficient querying by address and block time
    transactions.create_index(
        [("address", ASCENDING), ("status.block_time", DESCENDING)]
    )

    # Ensure the metadata collection has a document for the last processed block height
    if metadata.count_documents({"_id": "last_processed_block_height"}) == 0:
        metadata.insert_one({"_id": "last_processed_block_height", "height": 0})


def get_bitcoin_address_query_response_from_db(
    mongo_client: MongoClient, address: str
) -> Optional[BitcoinAddressQueryResponse]:
    """
    Get the query response for a Bitcoin address from the database.

    Parameters:
    - mongo_client: The MongoDB client instance
    - address: The Bitcoin address to query

    Returns:
    - The query response for the Bitcoin address
    """
    db = mongo_client[API_CACHE_DB]
    address_collection = db[ADDRESS_COLLECTION]
    transaction_collection = db[TRANSACTION_COLLECTION]
    query = {"address": address}

    address_dict = address_collection.find_one(query)
    if not address_dict:
        return None

    # Could have also used "status.block_height" if we had an index on it
    transactions = list(
        transaction_collection.find(query).sort("status.block_time", DESCENDING)
    )
    try:
        address_dict["transactions"] = [
            Transaction.model_validate(tx) for tx in transactions
        ]
    except ValidationError as e:
        logger.error(f"Error parsing transaction data for address {address}: {e}")
        return None

    try:
        query_response = BitcoinAddressQueryResponse.model_validate(address_dict)
        return query_response
    except ValidationError as e:
        logger.error(f"Error parsing address data for address {address}: {e}")
        return None


def add_bitcoin_address_query_response_to_db(
    mongo_client: MongoClient,
    query_response: BitcoinAddressQueryResponse,
    include_mempool: bool = False,
) -> Optional[str]:
    """
    Add (or update) the query response for a Bitcoin address to the database.

    Parameters:
    - mongo_client: The MongoDB client instance
    - query_response: The query response for the Bitcoin address
    - include_mempool: Whether to include mempool transactions in the cached response

    Returns:
    - error message if any, None if successful
    """
    db = mongo_client[API_CACHE_DB]
    address_collection = db[ADDRESS_COLLECTION]
    transaction_collection = db[TRANSACTION_COLLECTION]
    query = {"address": query_response.address}

    # Make a copy of the query response to avoid modifying the original object
    query_response = query_response.model_copy()

    if not include_mempool:
        query_response.transactions = [
            tx for tx in query_response.transactions if tx.status.confirmed
        ]
    transactions = query_response.transactions

    # Clear transactions from the address response to avoid duplication
    query_response.transactions = []

    # Dump by alias in case alias names are used in the model
    address_dict = query_response.model_dump(by_alias=True)

    # Remove the transactions field from the address_dict to avoid duplication
    address_dict.pop("transactions", None)

    try:
        address_collection.replace_one(query, address_dict, upsert=True)
    except PyMongoError as e:
        logger.error(f"Error updating address: {e}")
        return f"Error updating address: {e}"

    for transaction in transactions:
        transaction_dict = transaction.model_dump(by_alias=True)
        transaction_dict["address"] = query_response.address
        try:
            transaction_collection.replace_one(
                {"address": query_response.address, "txid": transaction.txid},
                transaction_dict,
                upsert=True,
            )
        except PyMongoError as e:
            logger.error(f"Error updating transaction {transaction.txid}: {e}")
            return f"Error updating transaction {transaction.txid}: {e}"

    return None


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
