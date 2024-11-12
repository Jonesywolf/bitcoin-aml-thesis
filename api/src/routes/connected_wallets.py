from fastapi import APIRouter, Request, HTTPException, status
from src.db.neo4j import get_connected_wallets_from_db
from src.models import ConnectedWallets
from neo4j import Driver

router = APIRouter()


@router.get("/{base58_address}", response_model=ConnectedWallets)
async def get_connected_wallets(
    request: Request, base58_address: str, force_update: bool = False
):
    neo4j_driver = request.app.state.neo4j_driver

    # Query the database for the connected wallets
    # Return the connected wallets

    # ? Should I really retrieve connected wallets for a wallet we don't have in the database?
    # ? Especially considering we add a wallet to the database when it is connected to another wallet
    # First, check if the wallet is in the database
    # If the wallet is not in the database, use an external API to get the data
    # Return the connected wallets
    # If the wallet is not found in the external API, return a 404 response
    # If the wallet is found in the external API, infer its class,
    # save it to the database and return the connected wallets

    # If the wallet is found, check to see if it is unpopulated, outdated or if force_update is True
    # If the wallet is unpopulated, outdated or force_update is True, use the external API to get the data
    # Update its class inference, and the connected wallets in the database
    # Return the updated connected wallets
    connected_wallets = get_connected_wallets_from_db(neo4j_driver, base58_address)

    if connected_wallets is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found in database"
        )
    else:
        return connected_wallets
