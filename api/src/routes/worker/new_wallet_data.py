from fastapi import APIRouter, Request, HTTPException, status
from src.ml.random_forest import infer_wallet_data_class
from src.extern.bitcoin_api import (
    get_wallet_data_from_api,
)
from src.db.neo4j import (
    get_wallet_data_from_db,
    upsert_connected_wallets_in_db,
    upsert_wallet_data_in_db,
)
from src.models import WalletData
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{base58_address}", response_model=WalletData)
async def get_new_wallet_data(
    request: Request, base58_address: str, force_update: bool = False
):
    # Query the database for the wallet data
    # * This is not strictly necessary, but it is a good practice to check the database first
    wallet_data = get_wallet_data_from_db(
        request.app.state.neo4j_driver, base58_address
    )

    # If the wallet is not found in the database, or its a stub added by connected wallets or if force_update is True
    # get the data from the external API directly
    if wallet_data is None or not wallet_data.is_populated or force_update:
        # Use an external API to get the data
        new_wallet_data, connected_wallets = await get_wallet_data_from_api(
            request.app.state.api_worker, request.app.state.mongo_client, base58_address
        )
        if new_wallet_data is None:
            # If the wallet is not found in the external API, return a 404 response
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
            )
        elif connected_wallets is None:
            # If the connected wallets are not found in the external API, return a 500 response
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error getting connected wallets",
            )
        else:
            # If the wallet is found in the external API, infer its class, save it to the database,
            # query the connections while you're at it and add those to the database too

            # Compute the inference for the wallet data
            new_wallet_data = infer_wallet_data_class(
                request.app.state.ml_session, new_wallet_data
            )

            # Add or update the wallet data and connected wallets to the database
            upsert_wallet_data_in_db(request.app.state.neo4j_driver, new_wallet_data)

            upsert_connected_wallets_in_db(
                request.app.state.neo4j_driver, base58_address, connected_wallets
            )

            return new_wallet_data

    # If the wallet is found in the database, check and it is populated, return the wallet data
    return wallet_data
