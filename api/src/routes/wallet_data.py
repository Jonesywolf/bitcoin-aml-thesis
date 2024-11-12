from fastapi import APIRouter, Request, HTTPException, status
from src.extern.bitcoin_api import (
    convert_to_wallet_data,
    get_address_data_from_api,
    get_wallet_data_from_api,
)
from src.db.neo4j import (
    get_wallet_data_from_db,
    update_wallet_data_in_db,
    add_wallet_data_to_db,
)
from src.models import WalletData
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{base58_address}", response_model=WalletData)
async def get_wallet_data(
    request: Request, base58_address: str, force_update: bool = False
):
    # Query the database for the wallet data
    wallet_data = None
    wallet_data = get_wallet_data_from_db(
        request.app.state.neo4j_driver, base58_address
    )
    # Get the raw address data from the API, saving postprocessing time if the wallet data is
    # up to date
    if wallet_data is not None and wallet_data.is_populated:
        # Check if the wallet data is outdated
        latest_wallet_data = get_address_data_from_api(base58_address)
        if wallet_data.total_txs != latest_wallet_data.n_tx or force_update:
            logger.info(f"Updating wallet data for {base58_address}")

            # Perform the required conversion and postprocessing to get the wallet data,
            # no need to make a new API call
            wallet_data, _ = convert_to_wallet_data(latest_wallet_data)
            # TODO: update the wallet data in the database, and update its class inference and connected wallets
            # update_wallet_data_in_db(request.app.state.neo4j_driver, wallet_data)
            # update_connected_wallets_in_db(request.app.state.neo4j_driver, base58_address, connected_wallets)
        return wallet_data

    # If the wallet is not found in the database, use an external API to get the data
    wallet_data, connected_wallets = get_wallet_data_from_api(base58_address)
    if wallet_data is None:
        # If the wallet is not found in the external API, return a 404 response
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
        )
    elif connected_wallets is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting connected wallets",
        )
    else:
        # If the wallet is found in the external API, infer its class, save it to the database,
        # query the connections while you're at it and those to the database too
        # TODO: Add the wallet data to the database
        # add_wallet_data_to_db(request.app.state.neo4j_driver, wallet_data)
        # TODO: Add the connected wallets to the database
        # update_connected_wallets_in_db(request.app.state.neo4j_driver, base58_address, connected_wallets)

        # Return the wallet data
        return wallet_data

    # If the wallet is found, check to see if it is unpopulated, outdated or if force_update is True
    # If the wallet is unpopulated, outdated or force_update is True, use the external API to get the data
    # Update the wallet data in the database, its class inference, and its connections
    # Return the updated wallet data

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not implemented"
    )
