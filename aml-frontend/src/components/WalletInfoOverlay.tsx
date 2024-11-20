import React from "react";
import { Button, Offcanvas, Table } from "react-bootstrap";
import { WalletData } from "../types/WalletData";
import { ArrowBarLeft } from "react-bootstrap-icons";

interface WalletInfoOverlayProps {
	walletData: WalletData | null;
	show: boolean;
	setShow: React.Dispatch<React.SetStateAction<boolean>>;
}

const WalletInfoOverlay: React.FC<WalletInfoOverlayProps> = ({
	walletData,
	show,
	setShow,
}) => {
	const handleClose = () => setShow(false);
	const handleShow = () => setShow(true);

	return (
		<>
			<Button
				variant="outline-secondary"
				onClick={handleShow}
				className="position-absolute top-0 mt-2 end-0 me-2"
			>
				<ArrowBarLeft size={24} />
			</Button>
			<Offcanvas
				show={show}
				onHide={handleClose}
				placement="end"
				scroll={true}
				backdrop={false}
				className="w-auto" // Ensure Offcanvas isn't horizontally scrollable when the table is rendered
				// ? Add opacity to the Offcanvas?
			>
				<Offcanvas.Header closeButton>
					<Offcanvas.Title>Wallet Information</Offcanvas.Title>
				</Offcanvas.Header>
				<Offcanvas.Body>
					{walletData != null ? (
						<Table striped bordered className="w-100">
							<thead>
								<tr>
									<th>Attribute</th>
									<th>Value</th>
								</tr>
							</thead>
							<tbody>
								<tr>
									<td>Node ID:</td>
									<td>{walletData.address}</td>
								</tr>
								<tr>
									<td># of Transactions as Sender:</td>
									<td>{walletData.num_txs_as_sender}</td>
								</tr>
								<tr>
									<td># of Transactions as Receiver:</td>
									<td>{walletData.num_txs_as_receiver}</td>
								</tr>
								<tr>
									<td>First Block Appeared In:</td>
									<td>{walletData.first_block_appeared_in}</td>
								</tr>
								<tr>
									<td>Last Block Appeared In:</td>
									<td>{walletData.last_block_appeared_in}</td>
								</tr>
								<tr>
									<td>Blocks Between Input Transactions Max:</td>
									<td>{walletData.blocks_btwn_input_txs_max}</td>
								</tr>
								<tr>
									<td>Blocks Between Input Transactions Mean:</td>
									<td>{walletData.blocks_btwn_input_txs_mean}</td>
								</tr>
								<tr>
									<td>Blocks Between Input Transactions Median:</td>
									<td>{walletData.blocks_btwn_input_txs_median}</td>
								</tr>
								<tr>
									<td>Blocks Between Input Transactions Min:</td>
									<td>{walletData.blocks_btwn_input_txs_min}</td>
								</tr>
								<tr>
									<td>Blocks Between Input Transactions Total:</td>
									<td>{walletData.blocks_btwn_input_txs_total}</td>
								</tr>
								<tr>
									<td>Blocks Between Output Transactions Max:</td>
									<td>{walletData.blocks_btwn_output_txs_max}</td>
								</tr>
								<tr>
									<td>Blocks Between Output Transactions Mean:</td>
									<td>{walletData.blocks_btwn_output_txs_mean}</td>
								</tr>
								<tr>
									<td>Blocks Between Output Transactions Median:</td>
									<td>{walletData.blocks_btwn_output_txs_median}</td>
								</tr>
								<tr>
									<td>Blocks Between Output Transactions Min:</td>
									<td>{walletData.blocks_btwn_output_txs_min}</td>
								</tr>
								<tr>
									<td>Blocks Between Output Transactions Total:</td>
									<td>{walletData.blocks_btwn_output_txs_total}</td>
								</tr>
								<tr>
									<td>Blocks Between Transactions Max:</td>
									<td>{walletData.blocks_btwn_txs_max}</td>
								</tr>
								<tr>
									<td>Blocks Between Transactions Mean:</td>
									<td>{walletData.blocks_btwn_txs_mean}</td>
								</tr>
								<tr>
									<td>Blocks Between Transactions Median:</td>
									<td>{walletData.blocks_btwn_txs_median}</td>
								</tr>
								<tr>
									<td>Blocks Between Transactions Min:</td>
									<td>{walletData.blocks_btwn_txs_min}</td>
								</tr>
								<tr>
									<td>Blocks Between Transactions Total:</td>
									<td>{walletData.blocks_btwn_txs_total}</td>
								</tr>
								<tr>
									<td>BTC Received Max:</td>
									<td>{walletData.btc_received_max}</td>
								</tr>
								<tr>
									<td>BTC Received Mean:</td>
									<td>{walletData.btc_received_mean}</td>
								</tr>
								<tr>
									<td>BTC Received Median:</td>
									<td>{walletData.btc_received_median}</td>
								</tr>
								<tr>
									<td>BTC Received Min:</td>
									<td>{walletData.btc_received_min}</td>
								</tr>
								<tr>
									<td>BTC Received Total:</td>
									<td>{walletData.btc_received_total}</td>
								</tr>
								<tr>
									<td>BTC Sent Max:</td>
									<td>{walletData.btc_sent_max}</td>
								</tr>
								<tr>
									<td>BTC Sent Mean:</td>
									<td>{walletData.btc_sent_mean}</td>
								</tr>
								<tr>
									<td>BTC Sent Median:</td>
									<td>{walletData.btc_sent_median}</td>
								</tr>
								<tr>
									<td>BTC Sent Min:</td>
									<td>{walletData.btc_sent_min}</td>
								</tr>
								<tr>
									<td>BTC Sent Total:</td>
									<td>{walletData.btc_sent_total}</td>
								</tr>
								<tr>
									<td>BTC Transacted Max:</td>
									<td>{walletData.btc_transacted_max}</td>
								</tr>
								<tr>
									<td>BTC Transacted Mean:</td>
									<td>{walletData.btc_transacted_mean}</td>
								</tr>
								<tr>
									<td>BTC Transacted Median:</td>
									<td>{walletData.btc_transacted_median}</td>
								</tr>
								<tr>
									<td>BTC Transacted Min:</td>
									<td>{walletData.btc_transacted_min}</td>
								</tr>
								<tr>
									<td>BTC Transacted Total:</td>
									<td>{walletData.btc_transacted_total}</td>
								</tr>
								<tr>
									<td>Class Inference:</td>
									<td>{walletData.class_inference}</td>
								</tr>
								<tr>
									<td>Fees as Share Max:</td>
									<td>{walletData.fees_as_share_max}</td>
								</tr>
								<tr>
									<td>Fees as Share Mean:</td>
									<td>{walletData.fees_as_share_mean}</td>
								</tr>
								<tr>
									<td>Fees as Share Median:</td>
									<td>{walletData.fees_as_share_median}</td>
								</tr>
								<tr>
									<td>Fees as Share Min:</td>
									<td>{walletData.fees_as_share_min}</td>
								</tr>
								<tr>
									<td>Fees as Share Total:</td>
									<td>{walletData.fees_as_share_total}</td>
								</tr>
								<tr>
									<td>Fees Max:</td>
									<td>{walletData.fees_max}</td>
								</tr>
								<tr>
									<td>Fees Mean:</td>
									<td>{walletData.fees_mean}</td>
								</tr>
								<tr>
									<td>Fees Median:</td>
									<td>{walletData.fees_median}</td>
								</tr>
								<tr>
									<td>Fees Min:</td>
									<td>{walletData.fees_min}</td>
								</tr>
								<tr>
									<td>Fees Total:</td>
									<td>{walletData.fees_total}</td>
								</tr>
								<tr>
									<td>First Received Block:</td>
									<td>{walletData.first_received_block}</td>
								</tr>
								<tr>
									<td>First Sent Block:</td>
									<td>{walletData.first_sent_block}</td>
								</tr>
								<tr>
									<td>Last Updated:</td>
									<td>{walletData.last_updated}</td>
								</tr>
								<tr>
									<td>Lifetime in Blocks:</td>
									<td>{walletData.lifetime_in_blocks}</td>
								</tr>
								<tr>
									<td>Number of Address Transacted Multiple:</td>
									<td>{walletData.num_addr_transacted_multiple}</td>
								</tr>
								<tr>
									<td>Total Transactions:</td>
									<td>{walletData.total_txs}</td>
								</tr>
								<tr>
									<td>Transacted with Address Max:</td>
									<td>{walletData.transacted_w_address_max}</td>
								</tr>
								<tr>
									<td>Transacted with Address Mean:</td>
									<td>{walletData.transacted_w_address_mean}</td>
								</tr>
								<tr>
									<td>Transacted with Address Median:</td>
									<td>{walletData.transacted_w_address_median}</td>
								</tr>
								<tr>
									<td>Transacted with Address Min:</td>
									<td>{walletData.transacted_w_address_min}</td>
								</tr>
								<tr>
									<td>Transacted with Address Total:</td>
									<td>{walletData.transacted_w_address_total}</td>
								</tr>
							</tbody>
						</Table>
					) : (
						<p>Click a Wallet to view its information</p>
					)}
				</Offcanvas.Body>
			</Offcanvas>
		</>
	);
};

export default WalletInfoOverlay;
