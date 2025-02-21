import aiohttp
import asyncio
import logging
import json
from typing import List, Optional
from pydantic import ValidationError
from fastapi import status

from src.models import (
    BitcoinAddressQueryResponse,
    Block,
    Transaction,
)

logger = logging.getLogger(__name__)


class BlockstreamAPIWorker:
    """
    A worker class that fetches data from the Blockstream API.

    The worker uses an asyncio queue to manage tasks and a single aiohttp session for all requests.
    It is designed to be used as a context manager to ensure proper cleanup.
    """

    BASE_URL = "https://blockstream.info/api/"
    RATE_LIMIT = 0.25  # seconds between requests

    def __init__(self):
        """
        Initialize the worker with an aiohttp session and a queue for tasks.
        """
        self.session = aiohttp.ClientSession()
        self.queue = asyncio.Queue()
        self.running = True
        self.worker_task = asyncio.create_task(self.worker())

    async def close(self):
        """
        Close the worker and cleanup resources.
        """
        self.running = False
        await self.queue.put(None)  # Signal the worker to stop
        await self.worker_task
        await self.session.close()

    async def fetch_address_data(
        self, base58_address: str
    ) -> Optional[BitcoinAddressQueryResponse]:
        """
        Fetch the information for a given Bitcoin address, no transactions included.

        Parameters:
        - base58_address: The base58 encoded Bitcoin address to query

        Returns:
        - The response data for the query
        """
        url = f"{self.BASE_URL}address/{base58_address}"
        async with self.session.get(url) as response:
            if response.status != status.HTTP_200_OK:
                logger.error(
                    f"Error fetching address data for {base58_address}: {response.status}"
                )
                return None
            try:
                data = await response.json()
                return BitcoinAddressQueryResponse.model_validate_json(json.dumps(data))
            except ValidationError as e:
                logger.error(
                    f"Error parsing address JSON response for BTC address: {base58_address}: {e}"
                )
                return None

    async def fetch_address_transactions(
        self, base58_address: str, last_seen_txid: Optional[str] = None
    ) -> List[Transaction]:
        """
        Fetch a page of transactions for a given Bitcoin address.

        Parameters:
        - base58_address: The base58 encoded Bitcoin address to query
        - last_seen_txid: The latest transaction ID to fetch transactions after

        Returns:
        - The list of transactions in the page
        """
        if last_seen_txid:
            url = f"{self.BASE_URL}address/{base58_address}/txs/chain/{last_seen_txid}"
        else:
            url = f"{self.BASE_URL}address/{base58_address}/txs"
        async with self.session.get(url) as response:
            if response.status != status.HTTP_200_OK:
                logger.error(
                    f"Error fetching address transactions for {base58_address}: {response.status}"
                )
                return None
            try:
                data = await response.json()
                transactions = [
                    Transaction.model_validate_json(json.dumps(tx)) for tx in data
                ]
                # Remove all transactions from the last_seen_txid onwards
                if last_seen_txid:
                    for i, tx in enumerate(transactions):
                        if tx.txid == last_seen_txid:
                            transactions = transactions[:i]
                            break
                return transactions
            except ValidationError as e:
                logger.error(
                    f"Error parsing address transactions JSON response for BTC address: {base58_address}: {e}"
                )
                return

    async def fetch_blocks(self) -> Optional[List[Block]]:
        """
        Fetch the list of the 10 latest blocks.

        Returns:
        - The list of the 10 latest blocks
        """
        url = f"{self.BASE_URL}blocks"
        async with self.session.get(url) as response:
            if response.status != status.HTTP_200_OK:
                logger.error(f"Failed to fetch blocks: {response.status}")
                return None
            try:
                blocks_data = await response.json()
                return [Block.model_validate_json(block) for block in blocks_data]
            except ValidationError as e:
                logger.error(f"Error parsing block data: {e}")
                return None

    async def fetch_latest_block_height(self) -> Optional[int]:
        """
        Fetch the latest block height.

        Returns:
        - The latest block height
        """
        url = f"{self.BASE_URL}blocks/tip/height"
        async with self.session.get(url) as response:
            if response.status != status.HTTP_200_OK:
                logger.error(f"Failed to fetch latest block height: {response.status}")
                return None
            try:
                data = await response.text()
                return int(data)
            except ValueError as e:
                logger.error(f"Error parsing block height: {e}")
                return None

    async def fetch_block_hash(self, block_height: int) -> Optional[str]:
        """
        Fetch the hash for a block at a given height.

        Parameters:
        - block_height: The block height to query

        Returns:
        - The hash of the block at the specified height
        """
        url = f"{self.BASE_URL}block-height/{block_height}"
        async with self.session.get(url) as response:
            if response.status != status.HTTP_200_OK:
                logger.error(
                    f"Failed to fetch block hash for block height {block_height}: {response.status}"
                )
                return None
            block_hash = await response.text()
            return block_hash

    async def fetch_block_transactions(
        self, block_hash: str, start_tx_idx: int = 0
    ) -> Optional[List[Transaction]]:
        """
        Fetch the transactions for a given block hash.

        Parameters:
        - block_hash: The hash of the block to query
        - start_tx_idx: The transaction index to start fetching transactions from, must be a multiple of 25

        Returns:
        - The list of transactions in the block
        """
        url = f"{self.BASE_URL}block/{block_hash}/txs/{start_tx_idx}"
        async with self.session.get(url) as response:
            response_text = await response.text()
        if (
            response.status == status.HTTP_404_NOT_FOUND
            and response_text == "start index out of range"
        ):
            return []  # No more transactions to fetch
        if response.status != status.HTTP_200_OK:
            logger.error(
                f"Failed to fetch transactions for block hash {block_hash}: {response.status}"
            )
            return None
        try:
            data = json.loads(
                response_text
            )  # Can't call response.json() after calling response.text()
            return [Transaction.model_validate_json(json.dumps(tx)) for tx in data]
        except (ValidationError, json.JSONDecodeError) as e:
            logger.error(
                f"Error parsing block transactions JSON response for block hash: {block_hash}: {e}"
            )
            return None

    async def worker(self):
        """
        The worker task that processes tasks from the queue.
        """
        while self.running:
            job = await self.queue.get()
            if job is None:
                break
            await job.run(self)
            self.queue.task_done()
            await asyncio.sleep(self.RATE_LIMIT)  # Respect rate limit

    async def add_to_queue(self, job):
        """
        Add a job to the queue.

        Parameters:
        - job: The job to add to the queue
        """
        await self.queue.put(job)


class Job:
    """
    Base class for jobs.
    """

    def __init__(self):
        """
        Initialize the job with a future.
        """
        self.future = asyncio.get_event_loop().create_future()

    async def run(self, worker: BlockstreamAPIWorker):
        """
        Run the job.

        Parameters:
        - worker: The BlockstreamAPIWorker instance

        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")


class AddressInformationJob(Job):
    """
    Job to get the first page of transactions and all associated information for a given Bitcoin address.
    """

    def __init__(self, base58_address: str):
        """
        Initialize the job with the address.

        Parameters:
        - base58_address: The base58 encoded Bitcoin address to query
        """
        super().__init__()
        self.base58_address = base58_address

    async def run(self, worker: BlockstreamAPIWorker):
        """
        Run the job to fetch the address information and transactions.

        Parameters:
        - worker: The BlockstreamAPIWorker instance

        Returns:
        - The BitcoinAddressQueryResponse with the first page of transactions and all associated information
        """
        address_info = await worker.fetch_address_data(self.base58_address)
        await asyncio.sleep(0.25)  # Respect rate limit
        if address_info:
            page_transactions = await worker.fetch_address_transactions(
                self.base58_address
            )
            if page_transactions:
                address_info.transactions = page_transactions
        self.future.set_result(address_info)


class TransactionRangeJob(Job):
    """
    Job to get transactions up to last_seen_txid for a given Bitcoin address.

    The transactions are fetched in pages of up to 25 transactions.
    """

    def __init__(self, base58_address: str, last_seen_txid: Optional[str]):
        """
        Initialize the job with the address and last_seen_txid.

        Parameters:
        - base58_address: The base58 encoded Bitcoin address to query
        - last_seen_txid: The latest transaction ID to fetch transactions after
        """
        super().__init__()
        self.base58_address = base58_address
        self.last_seen_txid = last_seen_txid

    async def run(self, worker: BlockstreamAPIWorker):
        """
        Run the job to fetch transactions up to last_seen_txid.

        Parameters:
        - worker: The BlockstreamAPIWorker instance

        Returns:
        - The list of transactions in the specified range
        """
        transactions = []
        last_seen_txid = self.last_seen_txid
        while True:
            page_transactions = await worker.fetch_address_transactions(
                self.base58_address, last_seen_txid
            )
            if not page_transactions:
                break
            # Prepend page_transactions to preserve order
            transactions = page_transactions + transactions
            if len(page_transactions) < 25:
                break
            last_seen_txid = page_transactions[-1].txid
            await asyncio.sleep(0.25)  # Respect rate limit
        self.future.set_result(transactions)


class BlocksJob(Job):
    """
    Job to get the list of blocks from the API.
    """

    async def run(self, worker: BlockstreamAPIWorker):
        """
        Run the job to fetch the list of the 10 latest blocks.

        Parameters:
        - worker: The BlockstreamAPIWorker instance

        Returns:
        - The list of the 10 latest blocks
        """
        blocks = await worker.fetch_blocks()
        self.future.set_result(blocks)


class LatestBlockHeightJob(Job):
    """
    Job to get the latest block height from the API.
    """

    async def run(self, worker: BlockstreamAPIWorker):
        """
        Run the job to fetch the latest block height.

        Parameters:
        - worker: The BlockstreamAPIWorker instance

        Returns:
        - The latest block height
        """
        block_height = await worker.fetch_latest_block_height()
        self.future.set_result(block_height)


class BlockHeightToHashJob(Job):
    """
    Job to get the hash for a block height from the API.
    """

    def __init__(self, block_height: int):
        """
        Initialize the job with the block height.

        Parameters:
        - block_height: The block height to query
        """
        super().__init__()
        self.block_height = block_height

    async def run(self, worker: BlockstreamAPIWorker):
        """
        Run the job to fetch the hash for the block height.

        Parameters:
        - worker: The BlockstreamAPIWorker instance

        Returns:
        - The hash of the block at the specified height
        """
        block_hash = await worker.fetch_block_hash(self.block_height)
        self.future.set_result(block_hash)


class BlockTransactionsJob(Job):
    """
    Job to get the transactions for a block from the API.
    """

    def __init__(self, block_hash: str, start_tx_idx: int = 0):
        """
        Initialize the job with the block hash and start block height.

        Parameters:
        - block_hash: The hash of the block to query
        - start_tx_id: The transaction index to start fetching transactions from, must be a multiple of 25
        """
        super().__init__()
        self.block_hash = block_hash
        self.start_tx_idx = start_tx_idx

    async def run(self, worker: BlockstreamAPIWorker):
        """
        Run the job to fetch the transactions for the block.

        Parameters:
        - worker: The BlockstreamAPIWorker instance

        Returns:
        - The list of transactions in the block
        """
        transactions = await worker.fetch_block_transactions(
            self.block_hash, self.start_tx_idx
        )
        self.future.set_result(transactions)


async def get_address_information(
    worker: BlockstreamAPIWorker, base58_address: str
) -> Optional[BitcoinAddressQueryResponse]:
    """
    Get the first page of transactions and all associated information for a given Bitcoin address.

    Parameters:
    - worker: The BlockchainAPIWorker instance
    - base58_address: The base58 encoded Bitcoin address to query

    Returns:
    - The BitcoinAddressQueryResponse with the first page of transactions and all associated information
    """
    job = AddressInformationJob(base58_address)
    await worker.add_to_queue(job)
    await job.future  # Wait for the specific job to complete
    return job.future.result()


async def get_transaction_range(
    worker: BlockstreamAPIWorker,
    base58_address: str,
    last_seen_txid: Optional[str] = None,
) -> List[Transaction]:
    """
    Get transactions up to last_seen_txid for a given Bitcoin address.

    Parameters:
    - worker: The BlockchainAPIWorker instance
    - base58_address: The base58 encoded Bitcoin address to query
    - last_seen_txid: The latest transaction ID to fetch transactions after

    Returns:
    - The list of transactions in the specified range
    """
    job = TransactionRangeJob(base58_address, last_seen_txid)
    await worker.add_to_queue(job)
    await job.future  # Wait for the specific job to complete
    return job.future.result()


async def get_latest_blocks(worker: BlockstreamAPIWorker) -> Optional[List[Block]]:
    """
    Get the list of the 10 latest blocks.

    Parameters:
    - worker: The BlockchainAPIWorker instance

    Returns:
    - The list of the 10 latest blocks
    """
    job = BlocksJob()
    await worker.add_to_queue(job)
    await job.future  # Wait for the specific job to complete
    return job.future.result()


async def get_latest_block_height(worker: BlockstreamAPIWorker) -> Optional[int]:
    """
    Get the latest block height.

    Parameters:
    - worker: The BlockchainAPIWorker instance
    """
    job = LatestBlockHeightJob()
    await worker.add_to_queue(job)
    await job.future  # Wait for the specific job to complete
    return job.future.result()


async def get_block_hash(
    worker: BlockstreamAPIWorker, block_height: int
) -> Optional[str]:
    """
    Get the hash for a block at a given height.

    Parameters:
    - worker: The BlockchainAPIWorker instance
    - block_height: The block height to query

    Returns:
    - The hash of the block at the specified height
    """
    job = BlockHeightToHashJob(block_height)
    await worker.add_to_queue(job)
    await job.future  # Wait for the specific job to complete
    return job.future.result()


async def get_block_transactions(
    worker: BlockstreamAPIWorker, block_hash: str, start_tx_idx: int = 0
) -> Optional[List[Transaction]]:
    """
    Get the transactions for a block from the API.

    Parameters:
    - worker: The BlockchainAPIWorker instance
    - block_hash: The hash of the block to query
    - start_tx_idx: The transaction index to start fetching transactions from, must be a multiple of 25

    Returns:
    - The list of transactions in the block
    """
    job = BlockTransactionsJob(block_hash, start_tx_idx)
    await worker.add_to_queue(job)
    await job.future  # Wait for the specific job to complete
    return job.future.result()
