from typing import Optional
from neo4j import Driver, ManagedTransaction
from src.models import WalletConnectionDetails, WalletData, ConnectedWallets


def get_wallet_data_from_db(
    neo4j_driver: Driver, base58_address: str
) -> Optional[WalletData]:
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
            if wallet_data_record["is_populated"] == False:
                return WalletData(
                    address=wallet_data_record["address"],
                    num_txs_as_sender=0,
                    num_txs_as_receiver=0,
                    first_block_appeared_in=0,
                    last_block_appeared_in=0,
                    lifetime_in_blocks=0,
                    total_txs=0,
                    first_sent_block=0,
                    first_received_block=0,
                    btc_transacted_total=0,
                    btc_transacted_min=0,
                    btc_transacted_max=0,
                    btc_transacted_mean=0,
                    btc_transacted_median=0,
                    btc_sent_total=0,
                    btc_sent_min=0,
                    btc_sent_max=0,
                    btc_sent_mean=0,
                    btc_sent_median=0,
                    btc_received_total=0,
                    btc_received_min=0,
                    btc_received_max=0,
                    btc_received_mean=0,
                    btc_received_median=0,
                    fees_total=0,
                    fees_min=0,
                    fees_max=0,
                    fees_mean=0,
                    fees_median=0,
                    fees_as_share_total=0,
                    fees_as_share_min=0,
                    fees_as_share_max=0,
                    fees_as_share_mean=0,
                    fees_as_share_median=0,
                    blocks_btwn_txs_total=0,
                    blocks_btwn_txs_min=0,
                    blocks_btwn_txs_max=0,
                    blocks_btwn_txs_mean=0,
                    blocks_btwn_txs_median=0,
                    blocks_btwn_input_txs_total=0,
                    blocks_btwn_input_txs_min=0,
                    blocks_btwn_input_txs_max=0,
                    blocks_btwn_input_txs_mean=0,
                    blocks_btwn_input_txs_median=0,
                    blocks_btwn_output_txs_total=0,
                    blocks_btwn_output_txs_min=0,
                    blocks_btwn_output_txs_max=0,
                    blocks_btwn_output_txs_mean=0,
                    blocks_btwn_output_txs_median=0,
                    num_addr_transacted_multiple=0,
                    transacted_w_address_total=0,
                    transacted_w_address_min=0,
                    transacted_w_address_max=0,
                    transacted_w_address_mean=0,
                    transacted_w_address_median=0,
                    class_inference=-1,
                    last_updated=wallet_data_record["last_updated"],
                    is_populated=False,
                )
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
                blocks_btwn_input_txs_total=wallet_data_record[
                    "blocks_btwn_input_txs_total"
                ],
                blocks_btwn_input_txs_min=wallet_data_record[
                    "blocks_btwn_input_txs_min"
                ],
                blocks_btwn_input_txs_max=wallet_data_record[
                    "blocks_btwn_input_txs_max"
                ],
                blocks_btwn_input_txs_mean=wallet_data_record[
                    "blocks_btwn_input_txs_mean"
                ],
                blocks_btwn_input_txs_median=wallet_data_record[
                    "blocks_btwn_input_txs_median"
                ],
                blocks_btwn_output_txs_total=wallet_data_record[
                    "blocks_btwn_output_txs_total"
                ],
                blocks_btwn_output_txs_min=wallet_data_record[
                    "blocks_btwn_output_txs_min"
                ],
                blocks_btwn_output_txs_max=wallet_data_record[
                    "blocks_btwn_output_txs_max"
                ],
                blocks_btwn_output_txs_mean=wallet_data_record[
                    "blocks_btwn_output_txs_mean"
                ],
                blocks_btwn_output_txs_median=wallet_data_record[
                    "blocks_btwn_output_txs_median"
                ],
                num_addr_transacted_multiple=wallet_data_record[
                    "num_addr_transacted_multiple"
                ],
                transacted_w_address_total=wallet_data_record[
                    "transacted_w_address_total"
                ],
                transacted_w_address_min=wallet_data_record["transacted_w_address_min"],
                transacted_w_address_max=wallet_data_record["transacted_w_address_max"],
                transacted_w_address_mean=wallet_data_record[
                    "transacted_w_address_mean"
                ],
                transacted_w_address_median=wallet_data_record[
                    "transacted_w_address_median"
                ],
                class_inference=wallet_data_record["class_inference"],
                last_updated=wallet_data_record["last_updated"],
                is_populated=wallet_data_record["is_populated"],
            )
            return wallet_data
    return None


def upsert_wallet_data_in_db(neo4j_driver: Driver, wallet_data: WalletData):
    """
    Add or update wallet data for a given Bitcoin wallet address in the Neo4j database.
    Creates the node if it doesn't exist, or updates it if it does.

    Parameters:
    - neo4j_driver: The Neo4j driver to use for the query
    - wallet_data: The wallet data to add or update in the database

    Returns:
    - True if the operation was successful
    """
    query = """
    MERGE (w:Wallet {address: $address})
    SET w = $wallet_data
    RETURN w
    """
    with neo4j_driver.session() as session:
        session.run(
            query,
            address=wallet_data.address,
            wallet_data=wallet_data.model_dump(),
        )
    return True


def get_connected_wallets_from_db(
    neo4j_driver: Driver, wallet_address: str
) -> Optional[ConnectedWallets]:
    """
    Get the connected wallets data for a given Bitcoin wallet address from the Neo4j database.

    Parameters:
    - neo4j_driver: The Neo4j driver to use for the query
    - wallet_address: The address of the wallet

    Returns:
    - The connected wallets data for the given wallet address, None if the wallet is not in the database
    """
    # Check if the wallet is in the database
    query = """
    MATCH (w:Wallet {address: $wallet_address})
    RETURN w
    """
    with neo4j_driver.session() as session:
        result = session.run(query, wallet_address=wallet_address)
        wallet_record = result.single()
        if wallet_record is None:
            return None

    # Retrieve the inbound connections first
    query = """
    MATCH (w:Wallet {address: $wallet_address})
    MATCH (w)-[r:TRANSACTED_WITH]->(cw:Wallet)
    RETURN cw.address AS address, r.num_transactions AS num_transactions, r.amount_transacted AS amount_transacted
    """
    MISSING_PROPERTY_PLACEHOLDER = -1

    connected_wallets = ConnectedWallets(
        wallet_address=wallet_address, inbound_connections={}, outbound_connections={}
    )
    with neo4j_driver.session() as session:
        result = session.run(query, wallet_address=wallet_address)
        for record in result:
            connected_wallets.inbound_connections[record["address"]] = (
                WalletConnectionDetails(
                    num_transactions=(
                        MISSING_PROPERTY_PLACEHOLDER
                        if record["num_transactions"] == None
                        else record["num_transactions"]
                    ),
                    amount_transacted=(
                        MISSING_PROPERTY_PLACEHOLDER
                        if record["amount_transacted"] == None
                        else record["amount_transacted"]
                    ),
                )
            )

    # Now retrieve the outbound connections
    query = """
    MATCH (w:Wallet {address: $wallet_address})
    MATCH (cw:Wallet)-[r:TRANSACTED_WITH]->(w)
    RETURN cw.address AS address, r.num_transactions AS num_transactions, r.amount_transacted AS amount_transacted
    """
    with neo4j_driver.session() as session:
        result = session.run(query, wallet_address=wallet_address)
        for record in result:
            connected_wallets.outbound_connections[record["address"]] = (
                WalletConnectionDetails(
                    num_transactions=(
                        MISSING_PROPERTY_PLACEHOLDER
                        if record["num_transactions"] == None
                        else record["num_transactions"]
                    ),
                    amount_transacted=(
                        MISSING_PROPERTY_PLACEHOLDER
                        if record["amount_transacted"] == None
                        else record["amount_transacted"]
                    ),
                )
            )

    return connected_wallets


def upsert_connected_wallets_in_db(
    neo4j_driver: Driver, wallet_address: str, connected_wallets: ConnectedWallets
):
    """
    Add or update the connected wallets data for a given Bitcoin wallet address to the Neo4j database.

    Parameters:
    - neo4j_driver: The Neo4j driver to use for the query
    - connected_wallets: The connected wallets data to add to the database
    """
    with neo4j_driver.session() as session:
        session.execute_write(
            _upsert_connected_wallets_in_db, wallet_address, connected_wallets
        )


def _upsert_connected_wallets_in_db(
    tx: ManagedTransaction, wallet_address: str, connected_wallets: ConnectedWallets
):
    """
    Add the connected wallets data for a given Bitcoin wallet address to the Neo4j database.

    Parameters:
    - tx: The Neo4j transaction to use for the query
    - wallet_address: The address of the wallet
    - connected_wallets: The connected wallets data to add to the database
    """
    # Create or update the main wallet node
    tx.run("MERGE (w:Wallet {address: $address})", address=wallet_address)

    # Create or update inbound connections
    for address, details in connected_wallets.inbound_connections.items():
        tx.run(
            """
            MERGE (w:Wallet {address: $wallet_address})
            MERGE (cw:Wallet {address: $connected_address})
            ON CREATE SET cw.is_populated = False, cw.last_updated = timestamp()
            MERGE (cw)-[r:TRANSACTED_WITH]->(w)
            ON CREATE SET r.num_transactions = $num_transactions, r.amount_transacted = $amount_transacted
            ON MATCH SET r.num_transactions = $num_transactions, r.amount_transacted = $amount_transacted
            """,
            wallet_address=wallet_address,
            connected_address=address,
            num_transactions=details.num_transactions,
            amount_transacted=details.amount_transacted,
        )

    # Create or update outbound connections
    for address, details in connected_wallets.outbound_connections.items():
        tx.run(
            """
            MERGE (w:Wallet {address: $wallet_address})
            MERGE (cw:Wallet {address: $connected_address})
            ON CREATE SET cw.populated = False, cw.last_updated = timestamp()
            MERGE (w)-[r:TRANSACTED_WITH]->(cw)
            ON CREATE SET r.num_transactions = $num_transactions, r.amount_transacted = $amount_transacted
            ON MATCH SET r.num_transactions = $num_transactions, r.amount_transacted = $amount_transacted
            """,
            wallet_address=wallet_address,
            connected_address=address,
            num_transactions=details.num_transactions,
            amount_transacted=details.amount_transacted,
        )
