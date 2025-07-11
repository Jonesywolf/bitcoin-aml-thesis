from time import time
from typing import List, Dict
from neo4j import Driver
from pymongo import MongoClient
from src.db.neo4j import (
    upsert_wallet_data_in_db,
    upsert_connected_wallets_in_db,
)
from src.extern.bitcoin_api import convert_to_wallet_data, get_address_data
from src.ml.random_forest import infer_wallet_data_class
from src.shared.ml_session import MLSession
from src.extern.api_worker import (
    BlockstreamAPIWorker,
    get_latest_block_height,
    get_block_hash,
    get_block_transactions,
    get_latest_blocks,
)
from src.db.mongodb import (
    ADDRESS_NEVER_PROCESSED,
    get_address_last_processed_block_height,
    get_last_processed_block_height,
    set_address_last_processed_block_height,
    set_last_processed_block_height,
)
from src.models import Block, Transaction
import logging
import asyncio

logger = logging.getLogger(__name__)


class BlockProcessingWorker:
    def __init__(
        self,
        mongo_client: MongoClient,
        api_worker: BlockstreamAPIWorker,
        ml_session: MLSession,
        neo4j_driver: Driver,
    ) -> None:
        """
        Initialize the block processing worker.

        Parameters:
        - mongo_client: The MongoDB client instance
        - api_worker: The API worker instance
        - ml_session: The machine learning session instance
        - neo4j_driver: The Neo4j driver instance
        """
        self.mongo_client = mongo_client
        self.api_worker = api_worker
        self.ml_session = ml_session
        self.neo4j_driver = neo4j_driver
        self._running = False

    async def start(self) -> None:
        """
        Start the block processing worker.
        """
        logger.info("Starting block processing worker")
        self._running = True
        while self._running:
            try:
                latest_block_height = await get_latest_block_height(self.api_worker)
                if latest_block_height is None:
                    logger.error("Error fetching latest block height, retrying...")
                    await asyncio.sleep(1)
                    continue

                last_processed_block_height = get_last_processed_block_height(
                    self.mongo_client
                )
                if last_processed_block_height is None:
                    logger.error(
                        "Error fetching last processed block height, retrying..."
                    )
                    await asyncio.sleep(1)
                    continue

                while last_processed_block_height < latest_block_height:
                    block_height = last_processed_block_height + 1
                    block_hash = await get_block_hash(self.api_worker, block_height)
                    if block_hash is None:
                        logger.error(
                            f"Error fetching block hash for block {block_height}, retrying..."
                        )
                        await asyncio.sleep(1)
                        continue
                    logger.info(
                        f"Processing block {block_height} with hash {block_hash}"
                    )

                    start_block_idx = 0
                    block_transactions = await get_block_transactions(
                        self.api_worker, block_hash, start_block_idx
                    )
                    while (
                        block_transactions is not None and len(block_transactions) != 0
                    ):
                        # * Don't strictly need to await here, but would need to be careful about concurrent access
                        # * to the DB
                        await self.process_block_transactions(
                            block_transactions,
                            last_processed_block_height,
                            latest_block_height,
                        )

                        start_block_idx += 25
                        block_transactions = await get_block_transactions(
                            self.api_worker, block_hash, start_block_idx
                        )

                    if block_transactions is None:
                        logger.error(
                            f"Error fetching transactions for block {block_height} with hash {block_hash}, retrying..."
                        )
                        await asyncio.sleep(1)
                        continue

                    set_last_processed_block_height(self.mongo_client, block_height)

                    last_processed_block_height = block_height

                latest_blocks = await get_latest_blocks(self.api_worker)
                if latest_blocks is None:
                    logger.error("Error fetching latest blocks, retrying...")
                    await asyncio.sleep(1)
                    continue

                processed_latest_block = True
                for block in latest_blocks:
                    if block.height > last_processed_block_height:
                        processed_latest_block = False
                        break  # Let the next iteration of the outer loop handle this block

                if processed_latest_block:
                    latest_block_timestamp = latest_blocks[0].timestamp
                    current_timestamp = int(time())
                    # Wait until ten minutes have passed since the latest block
                    if current_timestamp - latest_block_timestamp < 600:
                        await asyncio.sleep(
                            600 - (current_timestamp - latest_block_timestamp)
                        )
            except Exception as e:
                logger.error(f"Error in block processing worker: {e}")
                logger.exception(e)
                await asyncio.sleep(1)

    def stop(self) -> None:
        """
        Stop the block processing worker.
        """
        logger.info("Stopping block processing worker")
        self._running = False

    async def process_block_transactions(
        self,
        block_transactions: List[Transaction],
        last_processed_block_height: int,
        latest_block_height: int,
    ) -> None:
        """
        ! There are way more efficient ways to do this, but this is a good start
        ! ideally want a RW lock on the DB to prevent concurrent access
        ! ideally also do batch updates on wallets at the end of the block
        Process the transactions in a block.

        Parameters:
        - block_transactions: The list of transactions in the block
        - last_processed_block_height: The height of the last processed block
        - latest_block_height: The height of the latest block
        """
        # Collect unique addresses from transaction inputs and outputs
        unique_addresses = set()

        for tx in block_transactions:
            # Process input addresses
            for tx_input in tx.vin:
                if tx_input.prevout and tx_input.prevout.scriptpubkey_address:
                    unique_addresses.add(tx_input.prevout.scriptpubkey_address)

            # Process output addresses
            for tx_output in tx.vout:
                if tx_output.scriptpubkey_address:
                    unique_addresses.add(tx_output.scriptpubkey_address)

        # Process each unique address
        for address in unique_addresses:
            response = None
            address_last_processed_block_height = (
                get_address_last_processed_block_height(self.mongo_client, address)
            )
            if address_last_processed_block_height >= last_processed_block_height:
                continue  # This address has already been processed for this block

            response = await get_address_data(self.api_worker, address)
            if response is None:
                logger.error(f"Error fetching data for address {address}")
                continue

            # Update the MongoDB databaseM
            set_address_last_processed_block_height(
                self.mongo_client, address, latest_block_height
            )

            # Update in Neo4j
            wallet_data, connected_wallets = convert_to_wallet_data(response)

            # Compute the inference for the wallet data
            wallet_data = infer_wallet_data_class(self.ml_session, wallet_data)

            # Add or update the wallet data and connected wallets to the database
            upsert_wallet_data_in_db(self.neo4j_driver, wallet_data)
            upsert_connected_wallets_in_db(
                self.neo4j_driver, address, connected_wallets
            )
