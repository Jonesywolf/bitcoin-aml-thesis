import os

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
SETUP_MONGO_DB = os.getenv("SETUP_MONGO_DB", "False") == "True"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # or "DEBUG", "WARNING", "ERROR", "CRITICAL"
APPLICATION_TYPE_API = "API"
APPLICATION_TYPE_WORKER = "WORKER"
APPLICATION_TYPE = os.getenv("APPLICATION_TYPE", APPLICATION_TYPE_API)  # or "WORKER"

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
WORKER_API_URL = os.getenv("WORKER_API_URL", "http://127.0.0.1:8001")

# Route prefixes, could be shorter variable names
API_WALLET_ROUTE_PREFIX = "/wallet"
API_CONNECTED_WALLETS_ROUTE_PREFIX = "/connected-wallets"
WORKER_WALLET_ROUTE_PREFIX = "/wallet"
