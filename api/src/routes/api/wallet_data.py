from typing import Tuple
from fastapi import APIRouter, Request, HTTPException, status
from pydantic import ValidationError
from src.config import WORKER_API_URL, WORKER_WALLET_ROUTE_PREFIX
from src.db.neo4j import get_wallet_data_from_db
from src.models import ConnectedWallets, WalletData
import logging
import aiohttp

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{base58_address}", response_model=WalletData)
async def get_wallet_data(
    request: Request, base58_address: str, force_update: bool = False
):
    # Query the database for the wallet data
    wallet_data = get_wallet_data_from_db(
        request.app.state.neo4j_driver, base58_address
    )

    # If the wallet is not found in the database, or its a stub added by connected wallets or if force_update is True
    # get the data from the external API directly
    if wallet_data is None or not wallet_data.is_populated or force_update:
        # Use the worker to get the data from the Blockstream API
        new_wallet_data = await get_wallet_data_from_worker(base58_address)
        if new_wallet_data is None:
            # If the wallet is not found in the external API, return a 404 response
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
            )
        else:
            return new_wallet_data

    # If the wallet is found in the database, check and it is populated, return the wallet data
    return wallet_data


async def get_wallet_data_from_worker(
    base58_address: str,
) -> Tuple[WalletData]:
    """
    Get the wallet data from the worker.

    Parameters:
    - base58_address: The base58 encoded Bitcoin address to query

    Returns:
    - The wallet data
    """
    wallet_data = None

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{WORKER_API_URL}{WORKER_WALLET_ROUTE_PREFIX}/{base58_address}"
        ) as response:
            if response.status == 200:
                data = await response.json()
                try:
                    wallet_data = WalletData.model_validate(data)
                    return wallet_data
                except ValidationError as e:
                    logger.error(f"Error parsing validating parsed model: {e}")
                    return None, None
                except Exception as e:
                    logger.error(f"Error parsing JSON response: {e}")
                    return None, None
            elif response.status == 404:
                return None, None
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error getting data from worker",
                )

    return wallet_data
