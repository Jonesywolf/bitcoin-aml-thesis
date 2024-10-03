import logging

from fastapi import FastAPI
from src.routes import wallet_data
from src.routes import connected_wallets
from src.db.neo4j import lifespan

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

app.include_router(wallet_data.router, prefix="/wallet")
app.include_router(connected_wallets.router, prefix="/connected-wallets")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# * When we populate a wallet to the database, we will add its wallet connections too, but leave them unpopulated
# * by setting a flag in the database to False. When we query the database for a wallet, we will check if its connections
# * are populated, and if not, we will use the external API to get the data and populate the connections. We will also
# * update the connections when we update the wallet data.