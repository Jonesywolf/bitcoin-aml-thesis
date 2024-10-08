import logging
from contextlib import asynccontextmanager
from typing import Optional
from neo4j import Driver, GraphDatabase
from src.models import WalletData
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

def get_wallet_data_from_db(neo4j_driver: Driver, base58_address: str) -> Optional[WalletData]:
    """
    Get the wallet data for a given Bitcoin wallet address from the Neo4j database.
    
    Parameters:
    - neo4j_driver: The Neo4j driver to use for the query
    - base58_address: The base58 encoded Bitcoin wallet address
    
    Returns:
    - The wallet data for the given wallet address
    """
    query = """
    MATCH (w:Wallet {address: $base58_address})
    RETURN w
    """
    with neo4j_driver.session() as session:
        result = session.run(query, base58_address=base58_address)
        wallet_data_record = result.single()
        if wallet_data_record is not None:
            wallet_data_record = wallet_data_record["w"]
            wallet_data = WalletData(
                address=wallet_data_record["address"],
                num_txs_as_sender=wallet_data_record["num_txs_as_sender"],
                num_txs_as_receiver=wallet_data_record["num_txs_as_receiver"],
                first_block_appeared_in=wallet_data_record["first_block_appeared_in"],
                last_block_appeared_in=wallet_data_record["last_block_appeared_in"],
                lifetime_in_blocks=wallet_data_record["lifetime_in_blocks"],
                total_txs=wallet_data_record["total_txs"],
                first_sent_block=wallet_data_record["first_sent_block"],
                first_received_block=wallet_data_record["first_received_block"],
                btc_transacted_total=wallet_data_record["btc_transacted_total"],
                btc_transacted_min=wallet_data_record["btc_transacted_min"],
                btc_transacted_max=wallet_data_record["btc_transacted_max"],
                btc_transacted_mean=wallet_data_record["btc_transacted_mean"],
                btc_transacted_median=wallet_data_record["btc_transacted_median"],
                btc_sent_total=wallet_data_record["btc_sent_total"],
                btc_sent_min=wallet_data_record["btc_sent_min"],
                btc_sent_max=wallet_data_record["btc_sent_max"],
                btc_sent_mean=wallet_data_record["btc_sent_mean"],
                btc_sent_median=wallet_data_record["btc_sent_median"],
                btc_received_total=wallet_data_record["btc_received_total"],
                btc_received_min=wallet_data_record["btc_received_min"],
                btc_received_max=wallet_data_record["btc_received_max"],
                btc_received_mean=wallet_data_record["btc_received_mean"],
                btc_received_median=wallet_data_record["btc_received_median"],
                fees_total=wallet_data_record["fees_total"],
                fees_min=wallet_data_record["fees_min"],
                fees_max=wallet_data_record["fees_max"],
                fees_mean=wallet_data_record["fees_mean"],
                fees_median=wallet_data_record["fees_median"],
                fees_as_share_total=wallet_data_record["fees_as_share_total"],
                fees_as_share_min=wallet_data_record["fees_as_share_min"],
                fees_as_share_max=wallet_data_record["fees_as_share_max"],
                fees_as_share_mean=wallet_data_record["fees_as_share_mean"],
                fees_as_share_median=wallet_data_record["fees_as_share_median"],
                blocks_btwn_txs_total=wallet_data_record["blocks_btwn_txs_total"],
                blocks_btwn_txs_min=wallet_data_record["blocks_btwn_txs_min"],
                blocks_btwn_txs_max=wallet_data_record["blocks_btwn_txs_max"],
                blocks_btwn_txs_mean=wallet_data_record["blocks_btwn_txs_mean"],
                blocks_btwn_txs_median=wallet_data_record["blocks_btwn_txs_median"],
                blocks_btwn_input_txs_total=wallet_data_record["blocks_btwn_input_txs_total"],
                blocks_btwn_input_txs_min=wallet_data_record["blocks_btwn_input_txs_min"],
                blocks_btwn_input_txs_max=wallet_data_record["blocks_btwn_input_txs_max"],
                blocks_btwn_input_txs_mean=wallet_data_record["blocks_btwn_input_txs_mean"],
                blocks_btwn_input_txs_median=wallet_data_record["blocks_btwn_input_txs_median"],
                blocks_btwn_output_txs_total=wallet_data_record["blocks_btwn_output_txs_total"],
                blocks_btwn_output_txs_min=wallet_data_record["blocks_btwn_output_txs_min"],
                blocks_btwn_output_txs_max=wallet_data_record["blocks_btwn_output_txs_max"],
                blocks_btwn_output_txs_mean=wallet_data_record["blocks_btwn_output_txs_mean"],
                blocks_btwn_output_txs_median=wallet_data_record["blocks_btwn_output_txs_median"],
                num_addr_transacted_multiple=wallet_data_record["num_addr_transacted_multiple"],
                transacted_w_address_total=wallet_data_record["transacted_w_address_total"],
                transacted_w_address_min=wallet_data_record["transacted_w_address_min"],
                transacted_w_address_max=wallet_data_record["transacted_w_address_max"],
                transacted_w_address_mean=wallet_data_record["transacted_w_address_mean"],
                transacted_w_address_median=wallet_data_record["transacted_w_address_median"],
                class_inference=-1, # Placeholder value, will be updated later
                last_updated=wallet_data_record["last_updated"]
            )
            return wallet_data
    return None

def update_wallet_data_in_db(neo4j_driver: Driver, wallet_data: WalletData):
    """
    Update the wallet data for a given Bitcoin wallet address in the Neo4j database.
    
    Parameters:
    - neo4j_driver: The Neo4j driver to use for the query
    - wallet_data: The wallet data to update in the database
    """
    query = """
    MATCH (w:Wallet {address: $base58_address})
    SET w = $wallet_data
    RETURN w
    """
    with neo4j_driver.session() as session:
        session.run(query, base58_address=wallet_data.address, wallet_data=wallet_data.model_dump())

def add_wallet_data_to_db(neo4j_driver: Driver, wallet_data: WalletData):
    """
    Add the wallet data for a given Bitcoin wallet address to the Neo4j database.
    
    Parameters:
    - neo4j_driver: The Neo4j driver to use for the query
    - wallet_data: The wallet data to add to the database
    """
    query = """
    CREATE (w:Wallet $wallet_data)
    RETURN w
    """
    with neo4j_driver.session() as session:
        session.run(query, wallet_data=wallet_data.model_dump())