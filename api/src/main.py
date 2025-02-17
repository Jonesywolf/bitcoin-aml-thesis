import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.config import (
    API_CONNECTED_WALLETS_ROUTE_PREFIX,
    APPLICATION_TYPE_API,
    APPLICATION_TYPE_WORKER,
    LOG_LEVEL,
    APPLICATION_TYPE,
    WORKER_WALLET_ROUTE_PREFIX,
)
from src.routes.api import wallet_data
from src.routes.api import connected_wallets
from src.routes.worker import new_wallet_data
from src.shared.state import api_lifespan, worker_lifespan

# Configure logging
logging.basicConfig(level=LOG_LEVEL.upper())
logger = logging.getLogger(__name__)

if APPLICATION_TYPE == APPLICATION_TYPE_API:
    fastapi_lifespan = api_lifespan
elif APPLICATION_TYPE == APPLICATION_TYPE_WORKER:
    fastapi_lifespan = worker_lifespan
else:
    logger.fatal(f"Unknown application type: {APPLICATION_TYPE}")
    exit(1)


app = FastAPI(lifespan=fastapi_lifespan)

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

if APPLICATION_TYPE == APPLICATION_TYPE_API:
    app.include_router(wallet_data.router, prefix="/wallet")
    app.include_router(
        connected_wallets.router, prefix=API_CONNECTED_WALLETS_ROUTE_PREFIX
    )

elif APPLICATION_TYPE == APPLICATION_TYPE_WORKER:
    app.include_router(new_wallet_data.router, prefix=WORKER_WALLET_ROUTE_PREFIX)

if __name__ == "__main__":
    uvicorn.run(app)
