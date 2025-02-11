from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import numpy as np
from sklearn.preprocessing import MinMaxScaler


class WalletData(BaseModel):
    """
    A model representing various metrics and statistics related to a Bitcoin wallet.
    """

    address: str  # The Bitcoin wallet address
    num_txs_as_sender: float  # Number of transactions where this wallet is the sender
    num_txs_as_receiver: (
        float  # Number of transactions where this wallet is the receiver
    )
    first_block_appeared_in: float  # The block number where this wallet first appeared
    last_block_appeared_in: float  # The block number where this wallet last appeared
    lifetime_in_blocks: float  # The total number of blocks between the first and last appearance of this wallet
    total_txs: float  # The total number of transactions involving this wallet
    first_sent_block: (
        float  # The block number of the first transaction sent by this wallet
    )
    first_received_block: (
        float  # The block number of the first transaction received by this wallet
    )
    btc_transacted_total: float  # The total amount of Bitcoin transacted by this wallet
    btc_transacted_min: (
        float  # The minimum amount of Bitcoin transacted in a single transaction
    )
    btc_transacted_max: (
        float  # The maximum amount of Bitcoin transacted in a single transaction
    )
    btc_transacted_mean: float  # The mean amount of Bitcoin transacted per transaction
    btc_transacted_median: (
        float  # The median amount of Bitcoin transacted per transaction
    )
    btc_sent_total: float  # The total amount of Bitcoin sent by this wallet
    btc_sent_min: float  # The minimum amount of Bitcoin sent in a single transaction
    btc_sent_max: float  # The maximum amount of Bitcoin sent in a single transaction
    btc_sent_mean: float  # The mean amount of Bitcoin sent per transaction
    btc_sent_median: float  # The median amount of Bitcoin sent per transaction
    btc_received_total: float  # The total amount of Bitcoin received by this wallet
    btc_received_min: (
        float  # The minimum amount of Bitcoin received in a single transaction
    )
    btc_received_max: (
        float  # The maximum amount of Bitcoin received in a single transaction
    )
    btc_received_mean: float  # The mean amount of Bitcoin received per transaction
    btc_received_median: float  # The median amount of Bitcoin received per transaction
    fees_total: float  # The total transaction fees paid by this wallet
    fees_min: float  # The minimum transaction fee paid in a single transaction
    fees_max: float  # The maximum transaction fee paid in a single transaction
    fees_mean: float  # The mean transaction fee paid per transaction
    fees_median: float  # The median transaction fee paid per transaction
    fees_as_share_total: (
        float  # The total transaction fees as a share of the total amount sent
    )
    fees_as_share_min: float  # The minimum transaction fee as a share of the amount sent in a single transaction
    fees_as_share_max: float  # The maximum transaction fee as a share of the amount sent in a single transaction
    fees_as_share_mean: float  # The mean transaction fee as a share of the amount sent in a single transaction
    fees_as_share_median: float  # The median transaction fee as a share of the amount sent in a single transaction
    blocks_btwn_txs_total: (
        float  # The total number of blocks between transactions involving this wallet
    )
    blocks_btwn_txs_min: float  # The minimum number of blocks between transactions
    blocks_btwn_txs_max: float  # The maximum number of blocks between transactions
    blocks_btwn_txs_mean: float  # The mean number of blocks between transactions
    blocks_btwn_txs_median: float  # The median number of blocks between transactions
    blocks_btwn_input_txs_total: (
        float  # The total number of blocks between input transactions
    )
    blocks_btwn_input_txs_min: (
        float  # The minimum number of blocks between input transactions
    )
    blocks_btwn_input_txs_max: (
        float  # The maximum number of blocks between input transactions
    )
    blocks_btwn_input_txs_mean: (
        float  # The mean number of blocks between input transactions
    )
    blocks_btwn_input_txs_median: (
        float  # The median number of blocks between input transactions
    )
    blocks_btwn_output_txs_total: (
        float  # The total number of blocks between output transactions
    )
    blocks_btwn_output_txs_min: (
        float  # The minimum number of blocks between output transactions
    )
    blocks_btwn_output_txs_max: (
        float  # The maximum number of blocks between output transactions
    )
    blocks_btwn_output_txs_mean: (
        float  # The mean number of blocks between output transactions
    )
    blocks_btwn_output_txs_median: (
        float  # The median number of blocks between output transactions
    )
    num_addr_transacted_multiple: (
        float  # The number of addresses this wallet has transacted with multiple times
    )
    transacted_w_address_total: (
        float  # The total number of addresses this wallet has transacted with
    )
    transacted_w_address_min: (
        float  # The minimum number of addresses transacted with in a single transaction
    )
    transacted_w_address_max: (
        float  # The maximum number of addresses transacted with in a single transaction
    )
    transacted_w_address_mean: (
        float  # The mean number of addresses transacted with per transaction
    )
    transacted_w_address_median: (
        float  # The median number of addresses transacted with per transaction
    )
    class_inference: (
        int  # The class of the wallet as inferred by the model (0: licit, 1:illicit)
    )
    last_updated: int  # The unix timestamp of the last update to the wallet data
    is_populated: bool  # Indicates if the wallet data is fully populated or just a stub created by connected wallets

    def to_ml_model_input(self, min_max_scalers: Dict[str, MinMaxScaler]) -> np.ndarray:
        """
        Convert the wallet data object to a numpy array of its values, ignoring the address.

        Parameters:
        - min_max_scalers: The MinMax scalers used to preprocess the input data, indexed by feature name
        """

        # Selected Features for the model (in order):
        # ['btc_transacted_max', 'blocks_btwn_txs_min', 'fees_min', 'first_block_appeared_in', 'btc_transacted_mean', 'btc_transacted_median', 'fees_median', 'blocks_btwn_input_txs_total', 'blocks_btwn_txs_max', 'transacted_w_address_total', 'fees_total', 'fees_as_share_median', 'btc_transacted_min', 'fees_as_share_min', 'fees_as_share_mean', 'transacted_w_address_max', 'first_sent_block', 'lifetime_in_blocks', 'num_txs_as_sender', 'fees_as_share_max', 'transacted_w_address_mean', 'first_received_block', 'num_txs_as_receiver', 'fees_max', 'blocks_btwn_txs_total', 'transacted_w_address_median', 'fees_as_share_total', 'blocks_btwn_txs_mean', 'last_block_appeared_in', 'fees_mean']
        values = [
            min_max_scalers["btc_transacted_max"].transform(
                np.array([[self.btc_transacted_max]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["blocks_btwn_txs_min"].transform(
                np.array([[self.blocks_btwn_txs_min]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["fees_min"].transform(
                np.array([[self.fees_min]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["first_block_appeared_in"].transform(
                np.array([[self.first_block_appeared_in]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["btc_transacted_mean"].transform(
                np.array([[self.btc_transacted_mean]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["btc_transacted_median"].transform(
                np.array([[self.btc_transacted_median]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["fees_median"].transform(
                np.array([[self.fees_median]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["blocks_btwn_input_txs_total"].transform(
                np.array([[self.blocks_btwn_input_txs_total]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["blocks_btwn_txs_max"].transform(
                np.array([[self.blocks_btwn_txs_max]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["transacted_w_address_total"].transform(
                np.array([[self.transacted_w_address_total]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["fees_total"].transform(
                np.array([[self.fees_total]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["fees_as_share_median"].transform(
                np.array([[self.fees_as_share_median]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["btc_transacted_min"].transform(
                np.array([[self.btc_transacted_min]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["fees_as_share_min"].transform(
                np.array([[self.fees_as_share_min]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["fees_as_share_mean"].transform(
                np.array([[self.fees_as_share_mean]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["transacted_w_address_max"].transform(
                np.array([[self.transacted_w_address_max]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["first_sent_block"].transform(
                np.array([[self.first_sent_block]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["lifetime_in_blocks"].transform(
                np.array([[self.lifetime_in_blocks]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["num_txs_as_sender"].transform(
                np.array([[self.num_txs_as_sender]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["fees_as_share_max"].transform(
                np.array([[self.fees_as_share_max]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["transacted_w_address_mean"].transform(
                np.array([[self.transacted_w_address_mean]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["first_received_block"].transform(
                np.array([[self.first_received_block]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["num_txs_as_receiver"].transform(
                np.array([[self.num_txs_as_receiver]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["fees_max"].transform(
                np.array([[self.fees_max]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["blocks_btwn_txs_total"].transform(
                np.array([[self.blocks_btwn_txs_total]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["transacted_w_address_median"].transform(
                np.array([[self.transacted_w_address_median]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["fees_as_share_total"].transform(
                np.array([[self.fees_as_share_total]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["blocks_btwn_txs_mean"].transform(
                np.array([[self.blocks_btwn_txs_mean]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["last_block_appeared_in"].transform(
                np.array([[self.last_block_appeared_in]]).reshape(-1, 1)
            )[0][0],
            min_max_scalers["fees_mean"].transform(
                np.array([[self.fees_mean]]).reshape(-1, 1)
            )[0][0],
        ]

        return np.array(values)


class WalletConnectionDetails(BaseModel):
    """
    A model representing details of a connection between wallets.
    """

    num_transactions: int  # Number of transactions between the wallets
    amount_transacted: float  # Total amount transacted between the wallets


class ConnectedWallets(BaseModel):
    """
    A model representing information about wallets that have transacted with a given wallet.
    """

    wallet_address: str  # The address of the wallet

    inbound_connections: Dict[
        str, WalletConnectionDetails
    ]  # Wallets that have sent Bitcoin to the given wallet
    outbound_connections: Dict[
        str, WalletConnectionDetails
    ]  # Wallets that have received Bitcoin from the given wallet

    def is_empty(self):
        """
        Check if the connected wallets data is empty, that is, the wallet has no inbound or outbound connections.
        """
        return (
            len(self.inbound_connections) == 0 and len(self.outbound_connections) == 0
        )


class TransactionOutput(BaseModel):
    """
    Represents an output in a Bitcoin transaction.
    """

    scriptpubkey: str  # Script of the output
    scriptpubkey_asm: str  # ASM representation of the script
    scriptpubkey_type: str  # Type of the script (e.g., p2pkh, p2wsh)
    scriptpubkey_address: Optional[str] = None  # Associated Bitcoin address
    value: int  # Value of the output in satoshis


class TransactionInput(BaseModel):
    """
    Represents an input in a Bitcoin transaction.
    """

    txid: str  # Transaction ID of the previous transaction
    vout: int  # Index of the output being spent
    prevout: TransactionOutput  # Previous output details
    scriptsig: str  # ScriptSig used to unlock the output
    scriptsig_asm: str  # ASM representation of the scriptsig
    is_coinbase: bool  # Indicates if this input is a coinbase transaction
    sequence: int  # Sequence number
    # * Missing inner_redeemscript_asm, inner_witness_asm, and witness[] fields


class TransactionStatus(BaseModel):
    """
    Represents the confirmation status of a transaction.
    """

    confirmed: bool  # Whether the transaction is confirmed
    block_height: Optional[int] = (
        0  # Block height at which the transaction was confirmed
    )
    block_hash: Optional[str] = (
        None  # Hash of the block in which the transaction was confirmed
    )
    block_time: Optional[int] = (
        0  # Time at which the block was confirmed (UNIX timestamp)
    )


class Transaction(BaseModel):
    """
    Represents a Bitcoin transaction.
    """

    address: Optional[str] = (
        None  # The Bitcoin address queried, not in the API response, hence optional, necessary for MongoDB storage
    )
    txid: str  # Transaction ID
    version: int  # Transaction version
    locktime: int  # Lock time of the transaction
    vin: List[TransactionInput]  # List of transaction inputs
    vout: List[TransactionOutput]  # List of transaction outputs
    size: int  # Size of the transaction in bytes
    weight: int  # Weight of the transaction (used in SegWit)
    fee: int  # Transaction fee in satoshis
    status: TransactionStatus  # Transaction status (confirmed/unconfirmed)


class ChainStats(BaseModel):
    """
    Represents on-chain transaction statistics for a Bitcoin address.

    These statistics include details about funded and spent transaction outputs,
    as well as the total number of transactions associated with the address.
    """

    funded_txo_count: int  # Number of transaction outputs that funded the address
    funded_txo_sum: int  # Total value of funded transaction outputs in satoshis
    spent_txo_count: int  # Number of transaction outputs that were spent
    spent_txo_sum: int  # Total value of spent transaction outputs in satoshis
    tx_count: int  # Total number of transactions involving the address


class MempoolStats(BaseModel):
    """
    Represents mempool transaction statistics for a Bitcoin address.

    These statistics include transaction outputs that are in the mempool but
    have not yet been confirmed on-chain.
    """

    funded_txo_count: (
        int  # Number of transaction outputs funding the address in the mempool
    )
    funded_txo_sum: (
        int  # Total value of funded transaction outputs in the mempool (satoshis)
    )
    spent_txo_count: (
        int  # Number of transaction outputs spent from the address in the mempool
    )
    spent_txo_sum: (
        int  # Total value of spent transaction outputs in the mempool (satoshis)
    )
    tx_count: int  # Total number of transactions in the mempool involving the address


class BitcoinAddressQueryResponse(BaseModel):
    """
    Represents the response from a Blockstream API bitcoin address query.

    This includes details about the Bitcoin address, its on-chain statistics,
    and transactions that are currently in the mempool.
    """

    address: str  # The Bitcoin address queried
    chain_stats: ChainStats  # On-chain transaction statistics
    mempool_stats: MempoolStats  # Mempool transaction statistics
    # * Not in the API response, but we can add it here for convenience:
    transactions: Optional[List[Transaction]] = (
        []
    )  # List of transactions involving the address
    last_seen_txid: Optional[str] = (
        None  # The last transaction ID seen in the request, used for pagination
    )
    # We store the last seen txid to fetch the next page of transactions and
    # because we don't know the tie breaking rule when a wallet sends multiple
    # transactions in the same block
