from fastapi import APIRouter, Request, HTTPException, status
from src.extern.bitcoin_api import convert_to_wallet_data, get_address_data_from_api, get_wallet_data_from_api
from src.models import WalletData
from neo4j import Driver
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{base58_address}", response_model=WalletData)
async def get_wallet_data(request: Request, base58_address: str, force_update: bool = False):
    neo4j_driver = request.app.state.neo4j_driver
    
    # Query the database for the wallet data
    query = """
    MATCH (w:Wallet {address: $base58_address})
    RETURN w
    """
    wallet_data = None
    with neo4j_driver.session() as session:
        result = session.run(query, base58_address=base58_address)
        wallet_data_record = result.single()
        if wallet_data_record is not None:
            # ! We don't return it here because there will be a check to see if the number of transactions is 
            # ! the same as what the external API returns
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
                num_timesteps_appeared_in=wallet_data_record["num_timesteps_appeared_in"], # TODO: Remove
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
                class_inference=-1, # TODO: Infer the class using the ml model
                last_updated=0 # TODO: Add this field to the database
            )
            # Get the raw address data from the API, saving postprocessing time if the wallet data is
            # up to date
            if wallet_data is not None:
                # Check if the wallet data is outdated
                latest_wallet_data = get_address_data_from_api(base58_address)
                if wallet_data.total_txs != latest_wallet_data.n_tx:
                    logger.info(f"Updating wallet data for {base58_address}")
                    
                    # Perform the required conversion and postprocessing to get the wallet data,
                    # no need to make a new API call
                    wallet_data, _ = convert_to_wallet_data(latest_wallet_data)
                    # TODO: update the wallet data in the database, and update its class inference and connected wallets
                    # query = """
                    # MATCH (w:Wallet {address: $base58_address})
                    # SET w = $wallet_data
                    # RETURN w
                    # """
                    # with neo4j_driver.session() as session:
                    #     session.run(query, base58_address=base58_address, wallet_data=wallet_data.model_dump())
                
                return wallet_data
    
    # If the wallet is not found in the database, use an external API to get the data
    wallet_data, connected_wallets = get_wallet_data_from_api(base58_address)
    if wallet_data is None:
        # If the wallet is not found in the external API, return a 404 response
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    elif connected_wallets is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting connected wallets")
    else:
        # If the wallet is found in the external API, infer its class, save it to the database,
        # query the connections while you're at it and those to the database too
        # TODO: Add the wallet data to the database
        # query = """
        # CREATE (w:Wallet $wallet_data)
        # RETURN w
        # """
        # with neo4j_driver.session() as session:
        #     session.run(query, wallet_data=wallet_data.model_dump())
        
        # Return the wallet data
        return wallet_data
    
    
    
    
    # If the wallet is found, check to see if it is unpopulated, outdated or if force_update is True
    # If the wallet is unpopulated, outdated or force_update is True, use the external API to get the data
    # Update the wallet data in the database, its class inference, and its connections
    # Return the updated wallet data
    
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not implemented")