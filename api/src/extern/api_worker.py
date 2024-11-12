import aiohttp
import asyncio
import logging
import json
from typing import List, Optional
from pydantic import ValidationError
from fastapi import status

from src.models import (
    BitcoinAddressQueryResponse,
    Transaction,
)  # Assuming this model is defined in models.py

logger = logging.getLogger(__name__)


class BlockchainAPIWorker:
    """
    A worker class that fetches data from the Blockchain API.

    The worker uses an asyncio queue to manage tasks and a single aiohttp session for all requests.
    It is designed to be used as a context manager to ensure proper cleanup.
    """

    BASE_URL = "https://blockchain.info/rawaddr/"
    RATE_LIMIT = 10  # seconds between requests

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

    async def fetch_address_transactions(
        self, base58_address: str, offset: int = 0, limit: int = 100
    ) -> Optional[BitcoinAddressQueryResponse]:
        """
        Fetch a page of transactions for a given Bitcoin address.

        Parameters:
        - base58_address: The base58 encoded Bitcoin address to query
        - offset: The offset to use for the query
        - limit: The number of transactions to fetch

        Returns:
        - The response data for the query
        """
        url = f"{self.BASE_URL}{base58_address}?offset={offset}&limit={limit}"
        async with self.session.get(url) as response:
            if response.status != status.HTTP_200_OK:
                logger.error(
                    f"Error fetching data for {base58_address} with offset {offset}: {response.status}"
                )
                return None
            try:
                data = await response.json()
                return BitcoinAddressQueryResponse.model_validate_json(json.dumps(data))
            except ValidationError as e:
                logger.error(
                    f"Error parsing JSON response for BTC address: {base58_address} with offset {offset}: {e}"
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

    def __init__(self, base58_address: str):
        self.base58_address = base58_address
        self.future = asyncio.get_event_loop().create_future()

    async def run(self, worker: BlockchainAPIWorker):
        raise NotImplementedError("Subclasses must implement this method")


class AddressInformationJob(Job):
    """
    Job to get the first page of transactions and all associated information for a given Bitcoin address.
    """

    async def run(self, worker: BlockchainAPIWorker):
        address_info = await worker.fetch_address_transactions(self.base58_address, 0)
        self.future.set_result(address_info)


class TransactionRangeJob(Job):
    """
    Job to get a range of transactions for a given Bitcoin address.

    Parameters:
    - start: The starting index of the transactions to fetch
    - end: The ending index of the transactions to fetch
    """

    def __init__(self, base58_address: str, start: int, end: int):
        """
        Initialize the job with the address and range.

        Parameters:
        - base58_address: The base58 encoded Bitcoin address to query
        - start: The starting index of the transactions to fetch
        - end: The ending index of the transactions to fetch
        """
        super().__init__(base58_address)
        self.start = start
        self.end = end

    async def run(self, worker: BlockchainAPIWorker):
        transactions = []
        offset = self.start
        limit = 100
        while offset < self.end:
            page_data = await worker.fetch_address_transactions(
                self.base58_address, offset, limit
            )
            if not page_data or not page_data.txs:
                break
            transactions.extend(page_data.txs)
            offset += 100
            await asyncio.sleep(worker.RATE_LIMIT)  # Respect rate limit
        self.future.set_result(transactions)


async def get_address_information(
    worker: BlockchainAPIWorker, base58_address: str
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
    worker: BlockchainAPIWorker,
    base58_address: str,
    start: int,
    end: int,
) -> List[Transaction]:
    """
    Get a range of transactions for a given Bitcoin address.

    Parameters:
    - worker: The BlockchainAPIWorker instance
    - base58_address: The base58 encoded Bitcoin address to query
    - start: The starting index of the transactions to fetch
    - end: The ending index of the transactions to fetch

    Returns:
    - The list of transactions in the specified range
    """
    job = TransactionRangeJob(base58_address, start, end)
    await worker.add_to_queue(job)
    await job.future  # Wait for the specific job to complete
    return job.future.result()
