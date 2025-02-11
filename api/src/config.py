import os

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
SETUP_MONGO_DB = os.getenv("SETUP_MONGO_DB", "False") == "True"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # or "DEBUG", "WARNING", "ERROR", "CRITICAL"
APPLICATION_TYPE = os.getenv("APPLICATION_TYPE", "API")  # or "WORKER"
