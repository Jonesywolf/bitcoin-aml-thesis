from fastapi import APIRouter, Request, HTTPException, status
from src.models import WalletData
from neo4j import Driver

router = APIRouter()

@router.get("/{base58_address}", response_model=WalletData)
async def get_wallet(request: Request, base58_address: str):
    neo4j_driver = request.app.state.neo4j_driver
    
    # Query the database for the wallet data
    
    # If the wallet is not found, use an external API to get the data
    # Return the wallet data
    # If the wallet is not found in the external API, return a 404 response
    # If the wallet is found in the external API, infer its class, save it to the database,
    # query the connections while you're at it and those to the database too
    # Return the wallet data
    
    # If the wallet is found, check to see if it is unpopulated, outdated or if force_update is True
    # If the wallet is unpopulated, outdated or force_update is True, use the external API to get the data
    # Update the wallet data in the database, its class inference, and its connections
    # Return the updated wallet data
    
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not implemented")