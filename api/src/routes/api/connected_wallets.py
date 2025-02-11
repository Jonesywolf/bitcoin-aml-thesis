from fastapi import APIRouter, Request, HTTPException, status
from src.db.neo4j import get_connected_wallets_from_db
from src.models import ConnectedWallets

router = APIRouter()


@router.get("/{base58_address}", response_model=ConnectedWallets)
async def get_connected_wallets(request: Request, base58_address: str):
    neo4j_driver = request.app.state.neo4j_driver
    connected_wallets = get_connected_wallets_from_db(neo4j_driver, base58_address)

    if connected_wallets is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connected wallets not found in database",
        )
    else:
        return connected_wallets
