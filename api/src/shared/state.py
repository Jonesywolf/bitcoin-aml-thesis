import logging
from contextlib import asynccontextmanager
from neo4j import GraphDatabase
from src.extern.api_worker import BlockchainAPIWorker
from src.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app):
    """
    Allow access to the Neo4j database and the Blockchain.com API worker in the app state and manager
    their life cycles.
    
    Parameters:
    - app: The FastAPI application instance
    """
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    neo4j_driver.verify_connectivity()
    logger.info(f"Connected to Neo4j at {NEO4J_URI} as {NEO4J_USERNAME}")
    app.state.neo4j_driver = neo4j_driver
    
    blockchain_api_worker = BlockchainAPIWorker()
    logger.info("Started API worker")
    app.state.api_worker = blockchain_api_worker
    
    yield
    
    neo4j_driver.close()
    logger.info("Disconnected from Neo4j")
    
    await blockchain_api_worker.close()
    logger.info("Stopped API worker")