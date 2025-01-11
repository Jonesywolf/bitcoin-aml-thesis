export interface WalletData {
	address: string;
	num_txs_as_sender: number;
	num_txs_as_receiver: number;
	first_block_appeared_in: number;
	last_block_appeared_in: number;
	blocks_btwn_input_txs_max: number;
	blocks_btwn_input_txs_mean: number;
	blocks_btwn_input_txs_median: number;
	blocks_btwn_input_txs_min: number;
	blocks_btwn_input_txs_total: number;
	blocks_btwn_output_txs_max: number;
	blocks_btwn_output_txs_mean: number;
	blocks_btwn_output_txs_median: number;
	blocks_btwn_output_txs_min: number;
	blocks_btwn_output_txs_total: number;
	blocks_btwn_txs_max: number;
	blocks_btwn_txs_mean: number;
	blocks_btwn_txs_median: number;
	blocks_btwn_txs_min: number;
	blocks_btwn_txs_total: number;
	btc_received_max: number;
	btc_received_mean: number;
	btc_received_median: number;
	btc_received_min: number;
	btc_received_total: number;
	btc_sent_max: number;
	btc_sent_mean: number;
	btc_sent_median: number;
	btc_sent_min: number;
	btc_sent_total: number;
	btc_transacted_max: number;
	btc_transacted_mean: number;
	btc_transacted_median: number;
	btc_transacted_min: number;
	btc_transacted_total: number;
	class_inference: number;
	fees_as_share_max: number;
	fees_as_share_mean: number;
	fees_as_share_median: number;
	fees_as_share_min: number;
	fees_as_share_total: number;
	fees_max: number;
	fees_mean: number;
	fees_median: number;
	fees_min: number;
	fees_total: number;
	first_received_block: number;
	first_sent_block: number;
	last_updated: number;
	lifetime_in_blocks: number;
	num_addr_transacted_multiple: number;
	total_txs: number;
	transacted_w_address_max: number;
	transacted_w_address_mean: number;
	transacted_w_address_median: number;
	transacted_w_address_min: number;
	transacted_w_address_total: number;
}

/**
 * Determines the color of a node based on the class inference of the wallet data.
 *
 * @param walletData - The wallet data containing the class inference.
 * @returns The color of the node as a string. Returns "green" if class_inference is 0 (licit),
 *          "red" if class_inference is 1 (illicit), and "grey" for any other value (often -1 if unset).
 */
export function getNodeColor(walletData: WalletData): string {
	if (walletData.class_inference == 0) {
		return "green";
	} else if (walletData.class_inference == 1) {
		return "red";
	} else {
		return "grey";
	}
}
