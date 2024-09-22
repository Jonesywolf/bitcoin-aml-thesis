import logging
from contextlib import asynccontextmanager
from neo4j import GraphDatabase, Driver
from src.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    driver.verify_connectivity()
    logger.info(f"Connected to Neo4j at {NEO4J_URI} as {NEO4J_USERNAME}")
    
    app.state.neo4j_driver = driver
    
    yield
    
    driver.close()
    logger.info("Disconnected from Neo4j")