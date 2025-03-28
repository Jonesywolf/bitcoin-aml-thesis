import logging
from pydantic import ValidationError
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime
from typing import Optional, Tuple

from src.db.mongodb import set_address_last_processed_block_height
from src.extern.api_worker import (
    BlockstreamAPIWorker,
    get_address_information,
    get_transaction_range,
)
from src.models import (
    WalletData,
    WalletConnectionDetails,
    ConnectedWallets,
    BitcoinAddressQueryResponse,
    Transaction,
)

# Conversion factor from satoshis to BTC
SATOSHIS_TO_BTC = 1e-8
logger = logging.getLogger(__name__)


async def get_wallet_data_from_api(
    api_worker: BlockstreamAPIWorker,
    base58_address: str,
) -> Tuple[WalletData, ConnectedWallets]:
    """
    Convert the wallet data from the blockstream.info to a WalletData object.

    @param api_worker: The blockstream.com API worker instance.
    @param base58_address: The base58 encoded Bitcoin address to query.
    @return: The WalletData object populated with the data from the API.
    @return: The ConnectedWallets object populated with the connected wallets from the API.
    """
    address_data = await get_address_data(api_worker, base58_address)
    if address_data is None:
        return None, None

    wallet_data, connected_wallets = convert_to_wallet_data(address_data)

    # Update the last processed block height for the address in the database
    set_address_last_processed_block_height(
        api_worker, base58_address, address_data.transactions[0].status.block_height
    )
    return wallet_data, connected_wallets


async def get_address_data(
    api_worker: BlockstreamAPIWorker,
    base58_address: str,
    maximum_transactions: int = 20000,  # TODO: Fiddle with this number
) -> Optional[BitcoinAddressQueryResponse]:
    """
    Get the address data from the blockstream.com API

    @param base58_address: The base58 encoded Bitcoin address to query.
    @return: The BitcoinAddressQueryResponse object populated with the data from the API.
    """
    # Retrieve the address data from the cache if it exists
    latest_address_data = await get_address_information(api_worker, base58_address)

    # If the address data is not retrieved from the API or the cache is up to date,
    # return the cached data
    if latest_address_data is None:
        logger.error(f"Failed to retrieve data for address {base58_address}")
        return None
    else:
        # If the number of transactions is greater than 25, the API response is paginated
        # and the data is incomplete, so make new API calls until all transactions are retrieved
        if latest_address_data.chain_stats.tx_count > 25:
            logger.info(
                f"Address {base58_address} has more than 25 transactions: {latest_address_data.chain_stats.tx_count}"
            )
            if latest_address_data.chain_stats.tx_count > maximum_transactions:
                logger.error(
                    f"Address {base58_address} has {latest_address_data.chain_stats.tx_count} transactions, which exceeds the maximum of {maximum_transactions}."
                )
                return None  # ? Should we return the cached data here?
        address_transactions = await get_transaction_range(
            api_worker,
            base58_address,
            last_seen_txid=latest_address_data.transactions[-1].txid,
        )
        # Append the rest pf the transactions to preserve order
        latest_address_data.transactions.extend(address_transactions)

        # Store the last seen transaction ID in the cache for future updates
        latest_address_data.last_seen_txid = latest_address_data.transactions[0].txid

        return latest_address_data


def convert_to_wallet_data(
    address_query_response: BitcoinAddressQueryResponse,
    include_mempool: bool = False,
) -> Tuple[WalletData, ConnectedWallets]:
    """
    Converts a BitcoinAddressQueryResponse object to a WalletData object.

    Args:
        address_query_response (BitcoinAddressQueryResponse): The response from a Blockchain.com API bitcoin address query.

    Returns:
        WalletData: The populated WalletData object.
    """
    # Extract transactions
    transactions = address_query_response.transactions

    # Initialize variables for calculations
    total_txs = address_query_response.chain_stats.tx_count
    if include_mempool:
        total_txs += address_query_response.mempool_stats.tx_count

    num_txs_as_sender = 0
    num_txs_as_receiver = 0
    first_block_appeared_in = float("inf")
    last_block_appeared_in = float("-inf")
    last_block_sent_in = float("-inf")
    last_block_received_in = float("-inf")

    first_sent_block = float("inf")
    first_received_block = float("inf")
    btc_transacted_total = 0.0
    btc_transacted_min = float("inf")
    btc_transacted_max = float("-inf")
    btc_sent_total = 0.0
    btc_sent_min = float("inf")
    btc_sent_max = float("-inf")
    btc_received_total = 0.0
    btc_received_min = float("inf")
    btc_received_max = float("-inf")
    fees_total = 0.0
    fees_min = float("inf")
    fees_max = float("-inf")

    btc_transacted = []
    btc_sent = []
    btc_received = []
    btc_fees = []
    btc_fees_as_share = []
    blocks_btwn_txs = []
    blocks_btwn_input_txs = []
    blocks_btwn_output_txs = []
    addresses_transacted_with = defaultdict(int)  # address -> num_txs
    inbound_wallets = {}
    outbound_wallets = {}
    num_addresses_transacted_with = []
    transacted_w_address_total = 0

    # Process each transaction
    for tx in transactions:
        if not tx.status.confirmed and not include_mempool:
            continue

        num_addresses_transacted_with_this_tx = 0

        # Update blocks between transactions
        if last_block_appeared_in != float("-inf"):
            # Use absolute value since we're traversing the transactions in order from most to least recent
            blocks_btwn_txs.append(abs(tx.status.block_height - last_block_appeared_in))

        # Update first and last block appeared in
        first_block_appeared_in = min(first_block_appeared_in, tx.status.block_height)
        last_block_appeared_in = max(last_block_appeared_in, tx.status.block_height)

        # * Note that a transaction can show up as a sender and receiver and it can show up as an input or
        # * output more than once
        counted_this_tx_as_sender = False
        counted_this_tx_as_receiver = False

        # Create tx input and output dicts to handle the case where there is more than one input:
        # ex: bc1qpa35qq6xe57hxzru6xqlnr8u2fmvmxd8xfgx5z, txid: b6667f61edae55327a483a389a9d346675d85254f3737834eea7d7c16432efaf
        tx_input_dict = {}
        for tx_input in tx.vin:
            if (
                tx_input.prevout is None
                or tx_input.prevout.scriptpubkey_address is None
            ):
                continue
            if tx_input.prevout.scriptpubkey_address in tx_input_dict:
                tx_input_dict[
                    tx_input.prevout.scriptpubkey_address
                ] += tx_input.prevout.value
            else:
                tx_input_dict[tx_input.prevout.scriptpubkey_address] = (
                    tx_input.prevout.value
                )
        tx_output_dict = {}
        for tx_output in tx.vout:
            if tx_output.scriptpubkey_address is None:
                continue
            if tx_output.scriptpubkey_address in tx_output_dict:
                tx_output_dict[tx_output.scriptpubkey_address] += tx_output.value
            else:
                tx_output_dict[tx_output.scriptpubkey_address] = tx_output.value

        for tx_input in tx.vin:
            if (
                tx_input.prevout is None
                or tx_input.prevout.scriptpubkey_address is None
            ):
                continue
            if tx_input.prevout.scriptpubkey_address == address_query_response.address:
                if not counted_this_tx_as_sender:
                    num_txs_as_sender += 1
                    first_sent_block = min(first_sent_block, tx.status.block_height)

                    if last_block_sent_in != float("-inf"):
                        blocks_btwn_input_txs.append(
                            abs(tx.status.block_height - last_block_sent_in)
                        )
                    last_block_sent_in = tx.status.block_height

                    counted_this_tx_as_sender = True
                    btc_sent.append(tx_input.prevout.value)
                else:
                    btc_sent[-1] += tx_input.prevout.value

                # Update BTC fees (paid by sender)
                btc_fees.append(tx.fee)
                fees_total += tx.fee
                fees_min = min(fees_min, tx.fee)
                fees_max = max(fees_max, tx.fee)
            elif (
                address_query_response.address not in tx_input_dict
                or address_query_response.address in tx_output_dict
            ):  # If there are multiple inputs and this address is one of them, the other inputs
                # are not inbound connections unless this address is also a recipient in this transaction
                addr = tx_input.prevout.scriptpubkey_address
                num_addresses_transacted_with_this_tx += 1
                addresses_transacted_with[addr] += 1
                if addr in inbound_wallets:
                    inbound_wallets[addr].num_transactions += 1
                    inbound_wallets[addr].amount_transacted += (
                        tx_input.prevout.value * SATOSHIS_TO_BTC
                    )
                elif (
                    addr is not None
                ):  # Some transactions have no address in the API response
                    inbound_wallets[addr] = WalletConnectionDetails(
                        address=addr,
                        num_transactions=1,
                        amount_transacted=tx_input.prevout.value * SATOSHIS_TO_BTC,
                    )

        if counted_this_tx_as_sender:
            # Update sent BTC
            btc_sent_total += btc_sent[-1]
            btc_sent_min = min(btc_sent_min, btc_sent[-1])
            btc_sent_max = max(btc_sent_max, btc_sent[-1])

            # Update BTC fees as share of sent BTC
            btc_fees_as_share.append(tx.fee / btc_sent[-1])

        for tx_output in tx.vout:
            if tx_output.scriptpubkey_address is None:
                continue
            if tx_output.scriptpubkey_address == address_query_response.address:
                if not counted_this_tx_as_receiver:
                    num_txs_as_receiver += 1
                    if last_block_received_in != float("-inf"):
                        blocks_btwn_output_txs.append(
                            abs(tx.status.block_height - last_block_received_in)
                        )
                    last_block_received_in = tx.status.block_height

                    first_received_block = min(
                        first_received_block, tx.status.block_height
                    )
                    counted_this_tx_as_receiver = True

                    btc_received.append(tx_output.value)
                else:
                    btc_received[-1] += tx_output.value

            elif (
                counted_this_tx_as_sender
            ):  # Need to be the sender to have transacted with these other recipients
                addr = tx_output.scriptpubkey_address
                num_addresses_transacted_with_this_tx += 1
                addresses_transacted_with[addr] += 1
                if addr in outbound_wallets:
                    outbound_wallets[addr].num_transactions += 1
                    outbound_wallets[addr].amount_transacted += (
                        tx_output.value * SATOSHIS_TO_BTC
                    )
                elif (
                    addr is not None
                ):  # Some transactions have no address in the API response
                    outbound_wallets[addr] = WalletConnectionDetails(
                        address=addr,
                        num_transactions=1,
                        amount_transacted=tx_output.value * SATOSHIS_TO_BTC,
                    )

        if counted_this_tx_as_receiver:
            # Update received BTC
            btc_received_total += btc_received[-1]
            btc_received_min = min(btc_received_min, btc_received[-1])
            btc_received_max = max(btc_received_max, btc_received[-1])

        # Update BTC transacted
        btc_transacted_this_tx = 0
        if counted_this_tx_as_sender:
            btc_transacted_this_tx += btc_sent[-1]
        if counted_this_tx_as_receiver:
            btc_transacted_this_tx += btc_received[-1]

        btc_transacted.append(btc_transacted_this_tx)
        btc_transacted_total += abs(btc_transacted_this_tx)
        btc_transacted_min = min(btc_transacted_min, btc_transacted_this_tx)
        btc_transacted_max = max(btc_transacted_max, btc_transacted_this_tx)

        # Update num addresses transacted with
        num_addresses_transacted_with.append(num_addresses_transacted_with_this_tx)

    txs_with_amounts = len(btc_transacted)
    if txs_with_amounts == 0:
        btc_transacted_mean = 0
        btc_transacted_median = 0
    else:
        btc_transacted_mean = btc_transacted_total / txs_with_amounts
        txs_sorted_by_amount = sorted(btc_transacted)
        btc_transacted_median = txs_sorted_by_amount[txs_with_amounts // 2]

    if num_txs_as_sender == 0:
        btc_sent_mean = 0
        btc_sent_median = 0

    else:
        btc_sent_mean = btc_sent_total / num_txs_as_sender
        sent_values = sorted(btc_sent)
        btc_sent_median = sent_values[num_txs_as_sender // 2]

    if num_txs_as_receiver == 0:
        btc_received_mean = 0
        btc_received_median = 0
    else:
        btc_received_mean = btc_received_total / num_txs_as_receiver
        received_values = sorted(btc_received)
        btc_received_median = received_values[num_txs_as_receiver // 2]

    if num_txs_as_sender == 0:
        fees_mean = 0
        fees_median = 0
        fees_as_share_total = 0
        fees_as_share_min = 0
        fees_as_share_max = 0
        fees_as_share_mean = 0
        fees_as_share_median = 0
    else:
        fees_mean = fees_total / num_txs_as_sender
        fees_values = sorted(btc_fees)
        fees_median = fees_values[num_txs_as_sender // 2]

        fees_as_share_total = fees_total / btc_sent_total
        fees_as_share_min = min(btc_fees_as_share)
        fees_as_share_max = max(btc_fees_as_share)
        fees_as_share_mean = fees_mean / btc_sent_mean
        fees_as_share_median = fees_median / btc_sent_median

    if not blocks_btwn_txs:
        blocks_btwn_txs_total = 0
        blocks_btwn_txs_min = 0
        blocks_btwn_txs_max = 0
        blocks_btwn_txs_mean = 0
        blocks_btwn_txs_median = 0
    else:
        blocks_btwn_txs_total = sum(blocks_btwn_txs)
        blocks_btwn_txs_min = min(blocks_btwn_txs)
        blocks_btwn_txs_max = max(blocks_btwn_txs)
        blocks_btwn_txs_mean = blocks_btwn_txs_total / len(blocks_btwn_txs)
        blocks_btwn_txs_median = sorted(blocks_btwn_txs)[len(blocks_btwn_txs) // 2]

    if not blocks_btwn_input_txs:
        blocks_btwn_input_txs_total = 0
        blocks_btwn_input_txs_min = 0
        blocks_btwn_input_txs_max = 0
        blocks_btwn_input_txs_mean = 0
        blocks_btwn_input_txs_median = 0
    else:
        blocks_btwn_input_txs_total = sum(blocks_btwn_input_txs)
        blocks_btwn_input_txs_min = min(blocks_btwn_input_txs)
        blocks_btwn_input_txs_max = max(blocks_btwn_input_txs)
        blocks_btwn_input_txs_mean = blocks_btwn_input_txs_total / len(
            blocks_btwn_input_txs
        )
        blocks_btwn_input_txs_median = sorted(blocks_btwn_input_txs)[
            len(blocks_btwn_input_txs) // 2
        ]

    if not blocks_btwn_output_txs:
        blocks_btwn_output_txs_total = 0
        blocks_btwn_output_txs_min = 0
        blocks_btwn_output_txs_max = 0
        blocks_btwn_output_txs_mean = 0
        blocks_btwn_output_txs_median = 0
    else:
        blocks_btwn_output_txs_total = sum(blocks_btwn_output_txs)
        blocks_btwn_output_txs_min = min(blocks_btwn_output_txs)
        blocks_btwn_output_txs_max = max(blocks_btwn_output_txs)
        blocks_btwn_output_txs_mean = blocks_btwn_output_txs_total / len(
            blocks_btwn_output_txs
        )
        blocks_btwn_output_txs_median = sorted(blocks_btwn_output_txs)[
            len(blocks_btwn_output_txs) // 2
        ]

    if total_txs == 0 or not addresses_transacted_with:
        transacted_w_address_mean = 0
        transacted_w_address_median = 0
        transacted_w_address_min = 0
        transacted_w_address_max = 0
        num_addr_transacted_multiple = 0
    else:
        transacted_w_address_total = len(addresses_transacted_with)
        transacted_w_address_mean = transacted_w_address_total / total_txs
        sorted_num_addresses_transacted_with = sorted(num_addresses_transacted_with)
        transacted_w_address_median = sorted_num_addresses_transacted_with[
            len(sorted_num_addresses_transacted_with) // 2
        ]
        transacted_w_address_min = min(num_addresses_transacted_with)
        transacted_w_address_max = max(num_addresses_transacted_with)
        num_addr_transacted_multiple = sum(
            [1 for num in num_addresses_transacted_with if num > 1]
        )

    # Check for infinite or negative infinite values and replace with appropriate defaults
    # First block appeared
    if first_block_appeared_in == float("inf"):
        logger.info(
            f"Address {address_query_response.address}: first_block_appeared_in is infinity, setting to 0"
        )
        first_block_appeared_in = 0  # ? Should this be handled differently?

    # Last block appeared
    if last_block_appeared_in == float("-inf"):
        logger.info(
            f"Address {address_query_response.address}: last_block_appeared_in is -infinity, setting to 0"
        )
        last_block_appeared_in = 0  # ? Should this be handled differently?

    # First sent block
    if first_sent_block == float("inf"):
        logger.info(
            f"Address {address_query_response.address}: first_sent_block is infinity, setting to 0"
        )
        first_sent_block = 0  # ? Should this be handled differently?
    # First received block
    if first_received_block == float("inf"):
        logger.info(
            f"Address {address_query_response.address}: first_received_block is infinity, setting to 0"
        )
        first_received_block = 0

    # BTC transacted min
    if btc_transacted_min == float("inf"):
        logger.info(
            f"Address {address_query_response.address}: btc_transacted_min is infinity, setting to 0"
        )
        btc_transacted_min = 0

    # BTC sent min
    if btc_sent_min == float("inf"):
        logger.info(
            f"Address {address_query_response.address}: btc_sent_min is infinity, setting to 0"
        )
        btc_sent_min = 0

    # BTC received min
    if btc_received_min == float("inf"):
        logger.info(
            f"Address {address_query_response.address}: btc_received_min is infinity, setting to 0"
        )
        btc_received_min = 0

    # Fees min
    if fees_min == float("inf"):
        logger.info(
            f"Address {address_query_response.address}: fees_min is infinity, setting to 0"
        )
        fees_min = 0

    # BTC transacted max
    if btc_transacted_max == float("-inf"):
        logger.info(
            f"Address {address_query_response.address}: btc_transacted_max is -infinity, setting to 0"
        )
        btc_transacted_max = 0

    # BTC sent max
    if btc_sent_max == float("-inf"):
        logger.info(
            f"Address {address_query_response.address}: btc_sent_max is -infinity, setting to 0"
        )
        btc_sent_max = 0

    # BTC received max
    if btc_received_max == float("-inf"):
        logger.info(
            f"Address {address_query_response.address}: btc_received_max is -infinity, setting to 0"
        )
        btc_received_max = 0

    # Fees max
    if fees_max == float("-inf"):
        logger.info(
            f"Address {address_query_response.address}: fees_max is -infinity, setting to 0"
        )
        fees_max = 0

    # Create WalletData object
    wallet_data = WalletData(
        address=address_query_response.address,
        num_txs_as_sender=num_txs_as_sender,
        num_txs_as_receiver=num_txs_as_receiver,
        first_block_appeared_in=first_block_appeared_in,
        last_block_appeared_in=last_block_appeared_in,
        lifetime_in_blocks=last_block_appeared_in - first_block_appeared_in,
        total_txs=total_txs,
        first_sent_block=first_sent_block,
        first_received_block=first_received_block,
        btc_transacted_total=btc_transacted_total * SATOSHIS_TO_BTC,
        btc_transacted_min=btc_transacted_min * SATOSHIS_TO_BTC,
        btc_transacted_max=btc_transacted_max * SATOSHIS_TO_BTC,
        btc_transacted_mean=btc_transacted_mean * SATOSHIS_TO_BTC,
        btc_transacted_median=btc_transacted_median * SATOSHIS_TO_BTC,
        btc_sent_total=btc_sent_total * SATOSHIS_TO_BTC,
        btc_sent_min=btc_sent_min * SATOSHIS_TO_BTC,
        btc_sent_max=btc_sent_max * SATOSHIS_TO_BTC,
        btc_sent_mean=btc_sent_mean * SATOSHIS_TO_BTC,
        btc_sent_median=btc_sent_median * SATOSHIS_TO_BTC,
        btc_received_total=btc_received_total * SATOSHIS_TO_BTC,
        btc_received_min=btc_received_min * SATOSHIS_TO_BTC,
        btc_received_max=btc_received_max * SATOSHIS_TO_BTC,
        btc_received_mean=btc_received_mean * SATOSHIS_TO_BTC,
        btc_received_median=btc_received_median * SATOSHIS_TO_BTC,
        fees_total=fees_total * SATOSHIS_TO_BTC,
        fees_min=fees_min * SATOSHIS_TO_BTC,
        fees_max=fees_max * SATOSHIS_TO_BTC,
        fees_mean=fees_mean * SATOSHIS_TO_BTC,
        fees_median=fees_median * SATOSHIS_TO_BTC,
        fees_as_share_total=fees_as_share_total,
        fees_as_share_min=fees_as_share_min,
        fees_as_share_max=fees_as_share_max,
        fees_as_share_mean=fees_as_share_mean,
        fees_as_share_median=fees_as_share_median,
        blocks_btwn_txs_total=blocks_btwn_txs_total,
        blocks_btwn_txs_min=blocks_btwn_txs_min,
        blocks_btwn_txs_max=blocks_btwn_txs_max,
        blocks_btwn_txs_mean=blocks_btwn_txs_mean,
        blocks_btwn_txs_median=blocks_btwn_txs_median,
        blocks_btwn_input_txs_total=blocks_btwn_input_txs_total,
        blocks_btwn_input_txs_min=blocks_btwn_input_txs_min,
        blocks_btwn_input_txs_max=blocks_btwn_input_txs_max,
        blocks_btwn_input_txs_mean=blocks_btwn_input_txs_mean,
        blocks_btwn_input_txs_median=blocks_btwn_input_txs_median,
        blocks_btwn_output_txs_total=blocks_btwn_output_txs_total,
        blocks_btwn_output_txs_min=blocks_btwn_output_txs_min,
        blocks_btwn_output_txs_max=blocks_btwn_output_txs_max,
        blocks_btwn_output_txs_mean=blocks_btwn_output_txs_mean,
        blocks_btwn_output_txs_median=blocks_btwn_output_txs_median,
        num_addr_transacted_multiple=num_addr_transacted_multiple,
        transacted_w_address_total=transacted_w_address_total,
        transacted_w_address_min=transacted_w_address_min,
        transacted_w_address_max=transacted_w_address_max,
        transacted_w_address_mean=transacted_w_address_mean,
        transacted_w_address_median=transacted_w_address_median,
        class_inference=-1,  # Placeholder, this information will be inferred by the model later
        last_updated=int(datetime.now().timestamp()),
        is_populated=True,  # The data is populated from the API
    )

    connected_wallets = ConnectedWallets(
        wallet_address=address_query_response.address,
        inbound_connections=inbound_wallets,
        outbound_connections=outbound_wallets,
    )
    return wallet_data, connected_wallets
