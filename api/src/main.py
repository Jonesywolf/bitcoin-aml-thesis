import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.config import LOG_LEVEL, APPLICATION_TYPE
from src.routes.api import wallet_data
from src.routes.api import connected_wallets
from src.shared.state import lifespan

# Configure logging
logging.basicConfig(level=LOG_LEVEL.upper())
logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

# Configure CORS
origins = [
    "http://localhost:5173",
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

if APPLICATION_TYPE == "API":
    app.include_router(wallet_data.router, prefix="/wallet")
    app.include_router(connected_wallets.router, prefix="/connected-wallets")
elif APPLICATION_TYPE == "WORKER":
    pass  # TODO: Add worker routes
else:
    logger.fatal(f"Unknown application type: {APPLICATION_TYPE}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# * When we populate a wallet to the database, we will add its wallet connections too, but leave them unpopulated
# * by setting a flag in the database to False. When we query the database for a wallet, we will check if its connections
# * are populated, and if not, we will use the external API to get the data and populate the connections. We will also
# * update the connections when we update the wallet data.
