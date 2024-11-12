from pydantic import BaseModel, Field
from typing import Dict, List, Optional


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
        float  # The total transaction fees as a share of the total amount transacted
    )
    fees_as_share_min: float  # The minimum transaction fee as a share of the amount transacted in a single transaction
    fees_as_share_max: float  # The maximum transaction fee as a share of the amount transacted in a single transaction
    fees_as_share_mean: float  # The mean transaction fee as a share of the amount transacted per transaction
    fees_as_share_median: float  # The median transaction fee as a share of the amount transacted per transaction
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
    class_inference: int  # The class of the wallet as inferred by the model (1: illicit, 2:illicit, 3: unknown)
    last_updated: int  # The unix timestamp of the last update to the wallet data
    is_populated: bool  # Indicates if the wallet data is fully populated or just a stub created by connected wallets


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


class PreviousTransactionOutput(BaseModel):
    """
    Represents the previous output in a transaction input.
    """

    output_type: int = Field(..., alias="type")  # Type of the previous output
    spent: bool  # Indicates if the output has been spent
    value: int  # Value of the previous output in satoshis
    spending_outpoints: List[dict]  # List of spending outpoints
    n: int  # Index of the output in the transaction
    tx_index: int  # Transaction index
    script: str  # Script of the previous output
    addr: Optional[str]  # Address associated with the previous output


class TransactionInput(BaseModel):
    """
    Represents an input in a transaction.
    """

    sequence: int  # Sequence number of the input
    witness: str  # Witness data for the input
    script: str  # Script of the input
    index: int  # Index of the input in the transaction
    prev_out: PreviousTransactionOutput  # Previous output associated with the input


class TransactionOutput(BaseModel):
    """
    Represents an output in a transaction.
    """

    output_type: int = Field(..., alias="type")
    spent: bool  # Indicates if the output has been spent
    value: int  # Value of the output in satoshis
    spending_outpoints: List[dict]  # List of spending outpoints
    n: int  # Index of the output in the transaction
    tx_index: int  # Transaction index
    script: str  # Script of the output
    addr: Optional[str]  # Address associated with the output


class Transaction(BaseModel):
    """
    Represents a transaction in the blockchain.
    """

    hash: str  # Hash of the transaction
    ver: int  # Version of the transaction
    vin_sz: int  # Number of inputs in the transaction
    vout_sz: int  # Number of outputs in the transaction
    size: int  # Size of the transaction in bytes
    weight: int  # Weight of the transaction
    fee: int  # Fee for the transaction in satoshis
    relayed_by: str  # IP address of the node that relayed the transaction
    lock_time: int  # Lock time of the transaction
    tx_index: int  # Transaction index
    double_spend: bool  # Indicates if the transaction is a double spend
    time: int  # Timestamp of the transaction
    block_index: int  # Block index containing the transaction
    block_height: int  # Block height containing the transaction
    inputs: List[TransactionInput]  # List of inputs in the transaction
    out: List[TransactionOutput]  # List of outputs in the transaction
    result: int  # Result of the transaction
    balance: int  # Balance after the transaction


class BitcoinAddressQueryResponse(BaseModel):
    """
    Represents the response from a Blockchain.com API bitcoin address query.
    """

    hash160: str  # Hash160 of the address
    address: str  # Address string
    n_tx: int  # Number of transactions associated with the address
    n_unredeemed: int  # Number of unredeemed outputs
    total_received: int  # Total amount received by the address in satoshis
    total_sent: int  # Total amount sent by the address in satoshis
    final_balance: int  # Final balance of the address in satoshis
    txs: List[Transaction]  # List of transactions associated with the address
