from fastapi import APIRouter, Request, HTTPException, status
from src.models import ConnectedWallets
from neo4j import Driver

router = APIRouter()

@router.get("/{base58_address}", response_model=ConnectedWallets)
async def get_connected_wallets(request: Request, base58_address: str, force_update: bool = False):
    neo4j_driver = request.app.state.neo4j_driver
    
    # Query the database for the connected wallets
    # Return the connected wallets
    
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
    
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not implemented")