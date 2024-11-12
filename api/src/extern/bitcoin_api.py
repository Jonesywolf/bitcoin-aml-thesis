import json
import logging
import requests
from collections import defaultdict
from datetime import datetime
from pydantic import ValidationError
from typing import Tuple

from src.models import (
    WalletData,
    WalletConnectionDetails,
    ConnectedWallets,
    BitcoinAddressQueryResponse,
)

# Conversion factor from satoshis to BTC
SATOSHIS_TO_BTC = 1e-8
logger = logging.getLogger(__name__)


def get_wallet_data_from_api(
    base58_address: str,
) -> Tuple[WalletData, ConnectedWallets]:
    """
    Convert the wallet data from the Blockchain.com API to a WalletData object.

    @param base58_address: The base58 encoded Bitcoin address to query.
    @return: The WalletData object populated with the data from the API.
    @return: The ConnectedWallets object populated with the connected wallets from the API.
    """
    address_data = get_address_data_from_api(base58_address)
    if address_data is None:
        return None, None

    wallet_data, connected_wallets = convert_to_wallet_data(address_data)
    return wallet_data, connected_wallets


# TODO: Add pagination for transactions using &offset= and &limit=, note &limit= is capped at 100
def get_address_data_from_api(base58_address: str) -> BitcoinAddressQueryResponse:
    """
    Get the address data from the Blockchain.com API.

    @param base58_address: The base58 encoded Bitcoin address to query.
    @return: The BitcoinAddressQueryResponse object populated with the data from the API.
    """
    address_data = None
    response = requests.get(f"https://blockchain.info/rawaddr/{base58_address}")
    try:
        address_data = BitcoinAddressQueryResponse.model_validate_json(
            json.dumps(response.json())
        )
    except ValidationError as e:
        logger.error(
            f"Error parsing JSON response for BTC address: {base58_address}: {e}"
        )
        return None
    return address_data


def convert_to_wallet_data(
    address_query_response: BitcoinAddressQueryResponse,
) -> Tuple[WalletData, ConnectedWallets]:
    """
    Converts a BitcoinAddressQueryResponse object to a WalletData object.

    Args:
        address_query_response (BitcoinAddressQueryResponse): The response from a Blockchain.com API bitcoin address query.

    Returns:
        WalletData: The populated WalletData object.
    """
    # Extract transactions
    transactions = address_query_response.txs

    # Initialize variables for calculations
    num_txs_as_sender = 0
    num_txs_as_receiver = 0
    first_block_appeared_in = float("inf")
    last_block_appeared_in = float("-inf")
    total_txs = address_query_response.n_tx
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
        num_addresses_transacted_with_this_tx = 0
        btc_transacted.append(abs(tx.result))
        # Update first and last block appeared in
        first_block_appeared_in = min(first_block_appeared_in, tx.block_height)
        last_block_appeared_in = max(last_block_appeared_in, tx.block_height)

        # * Note that a transaction can show up as a sender and receiver and it can show up as an input or
        # * output more than once
        counted_this_tx_as_sender = False
        counted_this_tx_as_receiver = False
        for tx_input in tx.inputs:
            if tx_input.prev_out.addr == address_query_response.address:
                if not counted_this_tx_as_sender:
                    num_txs_as_sender += 1
                    first_sent_block = min(first_sent_block, tx.block_height)
                    blocks_btwn_input_txs.append(tx.block_height)
                    counted_this_tx_as_sender = True

                # Update sent BTC
                btc_sent.append(tx_input.prev_out.value)
                btc_sent_total += tx_input.prev_out.value
                btc_sent_min = min(btc_sent_min, tx_input.prev_out.value)
                btc_sent_max = max(btc_sent_max, tx_input.prev_out.value)

                # Update BTC fees (paid by sender)
                btc_fees.append(tx.fee)
                fees_total += tx.fee
                fees_min = min(fees_min, tx.fee)
                fees_max = max(fees_max, tx.fee)

                btc_fees_as_share.append(tx.fee / abs(tx.result))
            else:
                num_addresses_transacted_with_this_tx += 1
                addresses_transacted_with[tx_input.prev_out.addr] += 1
                if tx_input.prev_out.addr in outbound_wallets:
                    outbound_wallets[tx_input.prev_out.addr].num_transactions += 1
                    outbound_wallets[tx_input.prev_out.addr].amount_transacted += (
                        tx_input.prev_out.value * SATOSHIS_TO_BTC
                    )
                else:
                    outbound_wallets[tx_input.prev_out.addr] = WalletConnectionDetails(
                        address=tx_input.prev_out.addr,
                        num_transactions=1,
                        amount_transacted=tx_input.prev_out.value * SATOSHIS_TO_BTC,
                    )

        for tx_output in tx.out:
            if tx_output.addr == address_query_response.address:
                if not counted_this_tx_as_receiver:
                    num_txs_as_receiver += 1
                    blocks_btwn_output_txs.append(tx.block_height)
                    first_received_block = min(first_received_block, tx.block_height)
                    counted_this_tx_as_receiver = True

                # Update received BTC
                btc_received.append(tx_output.value)
                btc_received_total += tx_output.value
                btc_received_min = min(btc_received_min, tx_output.value)
                btc_received_max = max(btc_received_max, tx_output.value)
            else:
                num_addresses_transacted_with_this_tx += 1
                addresses_transacted_with[tx_output.addr] += 1
                if tx_output.addr in inbound_wallets:
                    inbound_wallets[tx_output.addr].num_transactions += 1
                    inbound_wallets[tx_output.addr].amount_transacted += (
                        tx_output.value * SATOSHIS_TO_BTC
                    )
                else:
                    inbound_wallets[tx_output.addr] = WalletConnectionDetails(
                        address=tx_output.addr,
                        num_transactions=1,
                        amount_transacted=tx_output.value * SATOSHIS_TO_BTC,
                    )

        # Update total BTC transacted
        btc_transacted_total += abs(tx.result)
        btc_transacted_min = min(btc_transacted_min, tx.result)
        btc_transacted_max = max(btc_transacted_max, tx.result)

        # Update num addresses transacted with
        num_addresses_transacted_with.append(num_addresses_transacted_with_this_tx)

    if total_txs == 0:
        btc_transacted_mean = 0
        btc_transacted_median = 0
    else:
        btc_transacted_mean = btc_transacted_total / total_txs
        txs_sorted_by_amount = sorted(btc_transacted)
        btc_transacted_median = txs_sorted_by_amount[total_txs // 2]

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

    if total_txs == 0:
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
            total_txs // 2
        ]
        transacted_w_address_min = min(num_addresses_transacted_with)
        transacted_w_address_max = max(num_addresses_transacted_with)
        num_addr_transacted_multiple = sum(
            [1 for num in num_addresses_transacted_with if num > 1]
        )

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
