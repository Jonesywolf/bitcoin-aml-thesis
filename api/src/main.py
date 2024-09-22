from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class WalletData(BaseModel):
    """
    A model representing various metrics and statistics related to a Bitcoin wallet.
    """
    address: str  # The Bitcoin wallet address
    num_txs_as_sender: int  # Number of transactions where this wallet is the sender
    num_txs_as_receiver: int  # Number of transactions where this wallet is the receiver
    first_block_appeared_in: int  # The block number where this wallet first appeared
    last_block_appeared_in: int  # The block number where this wallet last appeared
    lifetime_in_blocks: int  # The total number of blocks between the first and last appearance of this wallet
    total_txs: int  # The total number of transactions involving this wallet
    first_sent_block: int  # The block number of the first transaction sent by this wallet
    first_received_block: int  # The block number of the first transaction received by this wallet
    num_timesteps_appeared_in: int  # The number of distinct time steps this wallet appeared in (may not be necessary)
    btc_transacted_total: float  # The total amount of Bitcoin transacted by this wallet
    btc_transacted_min: float  # The minimum amount of Bitcoin transacted in a single transaction
    btc_transacted_max: float  # The maximum amount of Bitcoin transacted in a single transaction
    btc_transacted_mean: float  # The mean amount of Bitcoin transacted per transaction
    btc_transacted_median: float  # The median amount of Bitcoin transacted per transaction
    btc_sent_total: float  # The total amount of Bitcoin sent by this wallet
    btc_sent_min: float  # The minimum amount of Bitcoin sent in a single transaction
    btc_sent_max: float  # The maximum amount of Bitcoin sent in a single transaction
    btc_sent_mean: float  # The mean amount of Bitcoin sent per transaction
    btc_sent_median: float  # The median amount of Bitcoin sent per transaction
    btc_received_total: float  # The total amount of Bitcoin received by this wallet
    btc_received_min: float  # The minimum amount of Bitcoin received in a single transaction
    btc_received_max: float  # The maximum amount of Bitcoin received in a single transaction
    btc_received_mean: float  # The mean amount of Bitcoin received per transaction
    btc_received_median: float  # The median amount of Bitcoin received per transaction
    fees_total: float  # The total transaction fees paid by this wallet
    fees_min: float  # The minimum transaction fee paid in a single transaction
    fees_max: float  # The maximum transaction fee paid in a single transaction
    fees_mean: float  # The mean transaction fee paid per transaction
    fees_median: float  # The median transaction fee paid per transaction
    fees_as_share_total: float  # The total transaction fees as a share of the total amount transacted
    fees_as_share_min: float  # The minimum transaction fee as a share of the amount transacted in a single transaction
    fees_as_share_max: float  # The maximum transaction fee as a share of the amount transacted in a single transaction
    fees_as_share_mean: float  # The mean transaction fee as a share of the amount transacted per transaction
    fees_as_share_median: float  # The median transaction fee as a share of the amount transacted per transaction
    blocks_btwn_txs_total: int  # The total number of blocks between transactions involving this wallet
    blocks_btwn_txs_min: int  # The minimum number of blocks between transactions
    blocks_btwn_txs_max: int  # The maximum number of blocks between transactions
    blocks_btwn_txs_mean: float  # The mean number of blocks between transactions
    blocks_btwn_txs_median: float  # The median number of blocks between transactions
    blocks_btwn_input_txs_total: int  # The total number of blocks between input transactions
    blocks_btwn_input_txs_min: int  # The minimum number of blocks between input transactions
    blocks_btwn_input_txs_max: int  # The maximum number of blocks between input transactions
    blocks_btwn_input_txs_mean: float  # The mean number of blocks between input transactions
    blocks_btwn_input_txs_median: float  # The median number of blocks between input transactions
    blocks_btwn_output_txs_total: int  # The total number of blocks between output transactions
    blocks_btwn_output_txs_min: int  # The minimum number of blocks between output transactions
    blocks_btwn_output_txs_max: int  # The maximum number of blocks between output transactions
    blocks_btwn_output_txs_mean: float  # The mean number of blocks between output transactions
    blocks_btwn_output_txs_median: float  # The median number of blocks between output transactions
    num_addr_transacted_multiple: int  # The number of addresses this wallet has transacted with multiple times
    transacted_w_address_total: int  # The total number of addresses this wallet has transacted with
    transacted_w_address_min: int  # The minimum number of addresses transacted with in a single transaction
    transacted_w_address_max: int  # The maximum number of addresses transacted with in a single transaction
    transacted_w_address_mean: float  # The mean number of addresses transacted with per transaction
    transacted_w_address_median: float  # The median number of addresses transacted with per transaction
    class_inference: int # The class of the wallet as inferred by the model (1: illicit, 2:illicit, 3: unknown)
    last_updated: int  # The unix timestamp of the last update to the wallet data
    
class ConnectedWallets(BaseModel):
    connected_wallets: List[str]  # A list of Bitcoin wallet addresses connected to the wallet

# * When we populate a wallet to the database, we will add its wallet connections too, but leave them unpopulated
# * by setting a flag in the database to False. When we query the database for a wallet, we will check if its connections
# * are populated, and if not, we will use the external API to get the data and populate the connections. We will also
# * update the connections when we update the wallet data.

@app.get("/wallet-data/{base58_address}", response_model=WalletData)
async def get_wallet_data(base58_address: str, force_update: bool = False)  -> WalletData:
    # Query the database for the wallet data
    
    # If the wallet is not found, use an external API to get the data
    # Return the wallet data
    # If the wallet is not found in the external API, return a 404 response
    # If the wallet is found in the external API, infer its class, save it to the database,
    # query the connections while you're at it and those to the database too
    # Return the wallet data
    
    # If the wallet is found, check to see if it is unpopulated, outdated or if force_update is True
    # If the wallet is unpopulated, outdated or force_update is True, use the external API to get the data
    # Update the wallet data in the database, its class inference, and its connections
    # Return the updated wallet data
    
    raise NotImplementedError

@app.get("/connected-wallets/{base58_address}")
async def get_connected_wallets(base58_address: str, force_update: bool = False):
    # Query the database for the connected wallets
    # Return the connected wallets
    
    # First, check if the wallet is in the database
    # If the wallet is not in the database, use an external API to get the data
    # Return the connected wallets
    # If the wallet is not found in the external API, return a 404 response
    # If the wallet is found in the external API, infer its class, 
    # save it to the database and return the connected wallets
    
    # If the wallet is found, check to see if it is unpopulated, outdated or if force_update is True
    # If the wallet is unpopulated, outdated or force_update is True, use the external API to get the data
    # Update its class inference, and the connected wallets in the database
    # Return the updated connected wallets
    
    raise NotImplementedError