import { useEffect, useMemo, useRef, useState } from "react";
import { SigmaContainer, useSigma, useRegisterEvents } from "@react-sigma/core";
import { DirectedGraph } from "graphology";
import { useWorkerLayoutForce } from "@react-sigma/layout-force";
import { Coordinates } from "sigma/types";
import { EdgeArrowProgram } from "sigma/rendering";
import { EdgeCurvedArrowProgram } from "@sigma/edge-curve";

interface NodeData {
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

const GraphComponent = () => {
	const sigma = useSigma();
	const containerRef = useRef(null);

	useEffect(() => {
		const graph = new DirectedGraph();
		// Add some nodes
		graph.addNode("111112TykSw72ztDN2WJger4cynzWYC5w", {
			label: "111112TykSw72ztDN2WJger4cynzWYC5w",
			size: 25,
			color: "red",
			x: 0,
			y: 0,
		});
		graph.addNode("n2", {
			label: "Frank Sinatra: 1915",
			size: 25,
			color: "red",
			x: 10,
			y: 10,
		});
		graph.addNode("n3", {
			label: "Billie Holiday: 1915",
			size: 25,
			color: "red",
			x: 30,
			y: 10,
		});
		graph.addNode("n4", {
			label: "Louis Armstrong: 1901",
			size: 25,
			color: "yellow",
			x: 10,
			y: 10,
		});
		graph.addNode("n5", {
			label: "Nina Simone : 1933",
			size: 25,
			color: "orange",
			x: 30,
			y: 20,
		});
		graph.addNode("n6", {
			label: "Nat King Cole: 1919",
			size: 25,
			color: "red",
			x: 10,
			y: 0,
		});
		graph.addNode("n7", {
			label: "Gregory Porter: 1971",
			size: 25,
			color: "teal",
			x: 15,
			y: 15,
		});
		graph.addNode("n8", {
			label: "Sarah Vaughan: 1924",
			size: 25,
			color: "orange",
			x: 60,
			y: 60,
		});
		graph.addNode("n9", {
			label: "Michael Buble: 1975",
			size: 25,
			color: "teal",
			x: 10,
			y: 10,
		});

		graph.addEdge("111112TykSw72ztDN2WJger4cynzWYC5w", "n2", {
			size: 3,
			label: "60 BTC",
			type: "curved",
		});
		graph.addEdge("111112TykSw72ztDN2WJger4cynzWYC5w", "n3", {
			size: 3,
			label: "22 BTC",
			type: "curved",
		});
		graph.addEdge("111112TykSw72ztDN2WJger4cynzWYC5w", "n6", {
			size: 3,
			label: "1 BTC",
		});

		graph.addEdge("n2", "111112TykSw72ztDN2WJger4cynzWYC5w", {
			size: 3,
			label: "0.702 BTC",
			type: "curved",
		});
		graph.addEdge("n3", "111112TykSw72ztDN2WJger4cynzWYC5w", {
			size: 3,
			label: "0.24 BTC",
			type: "curved",
		});
		graph.addEdge("n5", "n8", { size: 3, label: "0.0003 BTC" });
		graph.addEdge("n7", "n9", { size: 3, label: "0.1 BTC" });

		if (sigma) {
			sigma.setGraph(graph);
			sigma.refresh();
		}
	}, [sigma]);

	return <div ref={containerRef} />;
};

const GraphEvents = ({
	setNodeData,
}: {
	setNodeData: React.Dispatch<React.SetStateAction<NodeData | null>>;
}) => {
	const sigma = useSigma();
	const registerEvents = useRegisterEvents();

	useEffect(() => {
		registerEvents({
			clickNode: async (event) => {
				console.log("Node clicked", event);
				const nodeId = event.node;

				// Send a web request to the backend
				const response = await fetch(`http://localhost:8000/wallet/${nodeId}`, {
					method: "GET",
					headers: {
						"Content-Type": "application/json",
					},
				});

				// Parse the response
				const data = await response.json();
				console.log(data);
				setNodeData(data);
			},
			clickStage: (event) => {
				console.log("Stage clicked", event);

				const graph = sigma.getGraph();
				const coords: Coordinates = sigma.viewportToGraph({
					x: event.event.x,
					y: event.event.y,
				});
				const id = `n${graph.order + 1}`;

				// Searching the two closest nodes to auto-create an edge to it
				const closestNodes = graph
					.nodes()
					.map((nodeId) => {
						const attrs = graph.getNodeAttributes(nodeId);
						const distance =
							Math.pow(coords.x - attrs.x, 2) + Math.pow(coords.y - attrs.y, 2);
						return { nodeId, distance };
					})
					.sort((a, b) => a.distance - b.distance)
					.slice(0, 2);

				graph.addNode(id, {
					label: `Node ${id}`,
					size: 25,
					color: "red",
					x: coords.x,
					y: coords.y,
				});

				closestNodes.forEach((node) => {
					graph.addEdge(id, node.nodeId);
				});
			},
		});
	}, [registerEvents, sigma, setNodeData]);
	return null;
};

const Fa2 = () => {
	const { start, kill } = useWorkerLayoutForce({
		settings: {},
	});

	useEffect(() => {
		// start FA2
		start();

		// Kill FA2 on unmount
		return () => {
			kill();
		};
	}, [start, kill]);

	return null;
};

const GraphWrapper = () => {
	// State to manage the node data for the overlay
	const [nodeData, setNodeData] = useState<NodeData | null>(null);

	// Sigma settings
	const settings = useMemo(
		() => ({
			renderEdgeLabels: true,
			defaultEdgeType: "straight",
			edgeProgramClasses: {
				straight: EdgeArrowProgram,
				curved: EdgeCurvedArrowProgram,
			},
		}),
		[]
	);

	return (
		<SigmaContainer settings={settings}>
			<GraphComponent />
			<GraphEvents setNodeData={setNodeData} />
			<Fa2 />
			{nodeData && (
				<div className="overlay">
					<h3>Node Information</h3>
					<table>
						<thead>
							<tr>
								<th>Attribute</th>
								<th>Value</th>
							</tr>
						</thead>
						<tbody>
							<tr>
								<td>Node ID:</td>
								<td>{nodeData.address}</td>
							</tr>
							<tr>
								<td># of Transactions as Sender:</td>
								<td>{nodeData.num_txs_as_sender}</td>
							</tr>
							<tr>
								<td># of Transactions as Receiver:</td>
								<td>{nodeData.num_txs_as_receiver}</td>
							</tr>
							<tr>
								<td>First Block Appeared In:</td>
								<td>{nodeData.first_block_appeared_in}</td>
							</tr>
							<tr>
								<td>Last Block Appeared In:</td>
								<td>{nodeData.last_block_appeared_in}</td>
							</tr>
							<tr>
								<td>Blocks Between Input Transactions Max:</td>
								<td>{nodeData.blocks_btwn_input_txs_max}</td>
							</tr>
							<tr>
								<td>Blocks Between Input Transactions Mean:</td>
								<td>{nodeData.blocks_btwn_input_txs_mean}</td>
							</tr>
							<tr>
								<td>Blocks Between Input Transactions Median:</td>
								<td>{nodeData.blocks_btwn_input_txs_median}</td>
							</tr>
							<tr>
								<td>Blocks Between Input Transactions Min:</td>
								<td>{nodeData.blocks_btwn_input_txs_min}</td>
							</tr>
							<tr>
								<td>Blocks Between Input Transactions Total:</td>
								<td>{nodeData.blocks_btwn_input_txs_total}</td>
							</tr>
							<tr>
								<td>Blocks Between Output Transactions Max:</td>
								<td>{nodeData.blocks_btwn_output_txs_max}</td>
							</tr>
							<tr>
								<td>Blocks Between Output Transactions Mean:</td>
								<td>{nodeData.blocks_btwn_output_txs_mean}</td>
							</tr>
							<tr>
								<td>Blocks Between Output Transactions Median:</td>
								<td>{nodeData.blocks_btwn_output_txs_median}</td>
							</tr>
							<tr>
								<td>Blocks Between Output Transactions Min:</td>
								<td>{nodeData.blocks_btwn_output_txs_min}</td>
							</tr>
							<tr>
								<td>Blocks Between Output Transactions Total:</td>
								<td>{nodeData.blocks_btwn_output_txs_total}</td>
							</tr>
							<tr>
								<td>Blocks Between Transactions Max:</td>
								<td>{nodeData.blocks_btwn_txs_max}</td>
							</tr>
							<tr>
								<td>Blocks Between Transactions Mean:</td>
								<td>{nodeData.blocks_btwn_txs_mean}</td>
							</tr>
							<tr>
								<td>Blocks Between Transactions Median:</td>
								<td>{nodeData.blocks_btwn_txs_median}</td>
							</tr>
							<tr>
								<td>Blocks Between Transactions Min:</td>
								<td>{nodeData.blocks_btwn_txs_min}</td>
							</tr>
							<tr>
								<td>Blocks Between Transactions Total:</td>
								<td>{nodeData.blocks_btwn_txs_total}</td>
							</tr>
							<tr>
								<td>BTC Received Max:</td>
								<td>{nodeData.btc_received_max}</td>
							</tr>
							<tr>
								<td>BTC Received Mean:</td>
								<td>{nodeData.btc_received_mean}</td>
							</tr>
							<tr>
								<td>BTC Received Median:</td>
								<td>{nodeData.btc_received_median}</td>
							</tr>
							<tr>
								<td>BTC Received Min:</td>
								<td>{nodeData.btc_received_min}</td>
							</tr>
							<tr>
								<td>BTC Received Total:</td>
								<td>{nodeData.btc_received_total}</td>
							</tr>
							<tr>
								<td>BTC Sent Max:</td>
								<td>{nodeData.btc_sent_max}</td>
							</tr>
							<tr>
								<td>BTC Sent Mean:</td>
								<td>{nodeData.btc_sent_mean}</td>
							</tr>
							<tr>
								<td>BTC Sent Median:</td>
								<td>{nodeData.btc_sent_median}</td>
							</tr>
							<tr>
								<td>BTC Sent Min:</td>
								<td>{nodeData.btc_sent_min}</td>
							</tr>
							<tr>
								<td>BTC Sent Total:</td>
								<td>{nodeData.btc_sent_total}</td>
							</tr>
							<tr>
								<td>BTC Transacted Max:</td>
								<td>{nodeData.btc_transacted_max}</td>
							</tr>
							<tr>
								<td>BTC Transacted Mean:</td>
								<td>{nodeData.btc_transacted_mean}</td>
							</tr>
							<tr>
								<td>BTC Transacted Median:</td>
								<td>{nodeData.btc_transacted_median}</td>
							</tr>
							<tr>
								<td>BTC Transacted Min:</td>
								<td>{nodeData.btc_transacted_min}</td>
							</tr>
							<tr>
								<td>BTC Transacted Total:</td>
								<td>{nodeData.btc_transacted_total}</td>
							</tr>
							<tr>
								<td>Class Inference:</td>
								<td>{nodeData.class_inference}</td>
							</tr>
							<tr>
								<td>Fees as Share Max:</td>
								<td>{nodeData.fees_as_share_max}</td>
							</tr>
							<tr>
								<td>Fees as Share Mean:</td>
								<td>{nodeData.fees_as_share_mean}</td>
							</tr>
							<tr>
								<td>Fees as Share Median:</td>
								<td>{nodeData.fees_as_share_median}</td>
							</tr>
							<tr>
								<td>Fees as Share Min:</td>
								<td>{nodeData.fees_as_share_min}</td>
							</tr>
							<tr>
								<td>Fees as Share Total:</td>
								<td>{nodeData.fees_as_share_total}</td>
							</tr>
							<tr>
								<td>Fees Max:</td>
								<td>{nodeData.fees_max}</td>
							</tr>
							<tr>
								<td>Fees Mean:</td>
								<td>{nodeData.fees_mean}</td>
							</tr>
							<tr>
								<td>Fees Median:</td>
								<td>{nodeData.fees_median}</td>
							</tr>
							<tr>
								<td>Fees Min:</td>
								<td>{nodeData.fees_min}</td>
							</tr>
							<tr>
								<td>Fees Total:</td>
								<td>{nodeData.fees_total}</td>
							</tr>
							<tr>
								<td>First Received Block:</td>
								<td>{nodeData.first_received_block}</td>
							</tr>
							<tr>
								<td>First Sent Block:</td>
								<td>{nodeData.first_sent_block}</td>
							</tr>
							<tr>
								<td>Last Updated:</td>
								<td>{nodeData.last_updated}</td>
							</tr>
							<tr>
								<td>Lifetime in Blocks:</td>
								<td>{nodeData.lifetime_in_blocks}</td>
							</tr>
							<tr>
								<td>Number of Address Transacted Multiple:</td>
								<td>{nodeData.num_addr_transacted_multiple}</td>
							</tr>
							<tr>
								<td>Total Transactions:</td>
								<td>{nodeData.total_txs}</td>
							</tr>
							<tr>
								<td>Transacted with Address Max:</td>
								<td>{nodeData.transacted_w_address_max}</td>
							</tr>
							<tr>
								<td>Transacted with Address Mean:</td>
								<td>{nodeData.transacted_w_address_mean}</td>
							</tr>
							<tr>
								<td>Transacted with Address Median:</td>
								<td>{nodeData.transacted_w_address_median}</td>
							</tr>
							<tr>
								<td>Transacted with Address Min:</td>
								<td>{nodeData.transacted_w_address_min}</td>
							</tr>
							<tr>
								<td>Transacted with Address Total:</td>
								<td>{nodeData.transacted_w_address_total}</td>
							</tr>
						</tbody>
					</table>
				</div>
			)}
		</SigmaContainer>
	);
};

export default GraphWrapper;
