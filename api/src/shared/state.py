import logging
from contextlib import asynccontextmanager
from neo4j import GraphDatabase
from pymongo import MongoClient
from src.db.mongodb import set_up_database
from src.extern.api_worker import BlockchainAPIWorker
from src.config import (
    MONGO_URI,
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
    SETUP_MONGO_DB,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    """
    Allow access to the Neo4j database and the Blockchain.com API worker in the app state and manager
    their life cycles.

    Parameters:
    - app: The FastAPI application instance
    """
    neo4j_driver = GraphDatabase.driver(
        NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )
    neo4j_driver.verify_connectivity()
    logger.info(f"Connected to Neo4j at {NEO4J_URI} as {NEO4J_USERNAME}")
    app.state.neo4j_driver = neo4j_driver

    mongo_client = MongoClient(MONGO_URI)
    logger.info(f"Connected to MongoDB at {MONGO_URI}")
    app.state.mongo_client = mongo_client

    if SETUP_MONGO_DB:
        set_up_database(mongo_client)
        logger.info("Set up MongoDB database")

    blockchain_api_worker = BlockchainAPIWorker()
    logger.info("Started API worker")
    app.state.api_worker = blockchain_api_worker

    yield

    neo4j_driver.close()
    logger.info("Disconnected from Neo4j")

    mongo_client.close()
    logger.info("Disconnected from MongoDB")

    await blockchain_api_worker.close()
    logger.info("Stopped API worker")
