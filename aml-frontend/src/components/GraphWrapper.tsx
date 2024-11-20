import { useEffect, useMemo, useRef, useState } from "react";
import {
	SigmaContainer,
	useSigma,
	useRegisterEvents,
	ControlsContainer,
	ZoomControl,
	FullScreenControl,
} from "@react-sigma/core";
import { DirectedGraph } from "graphology";
import { EdgeArrowProgram } from "sigma/rendering";
import { EdgeCurvedArrowProgram } from "@sigma/edge-curve";
import { WalletData } from "../types/WalletData";
import WalletInfoOverlay from "./WalletInfoOverlay";
import ForceAtlasLayout from "./ForceAtlasLayout";
import InitialModal from "./InitialModal";
import { Button } from "react-bootstrap";
import { MoonFill, SunFill } from "react-bootstrap-icons";
import ConnectedWallets from "../types/ConnectedWallets";
import { Coordinates } from "sigma/types";

const GraphComponent = () => {
	const sigma = useSigma();
	const containerRef = useRef(null);

	useEffect(() => {
		const graph = new DirectedGraph();

		if (sigma) {
			sigma.setGraph(graph);
			sigma.refresh();
		}
	}, [sigma]);

	return <div ref={containerRef} />;
};

const GraphEvents = ({
	setWalletData,
	setShowOverlay,
}: {
	setWalletData: React.Dispatch<React.SetStateAction<WalletData | null>>;
	setShowOverlay: React.Dispatch<React.SetStateAction<boolean>>;
}) => {
	const sigma = useSigma();
	const registerEvents = useRegisterEvents();

	useEffect(() => {
		registerEvents({
			clickNode: (event) => {
				(async () => {
					const nodeId = event.node;
					console.log(`Node: ${nodeId} clicked`, event);

					// Send a web request to the backend
					const response = await fetch(
						`http://localhost:8000/wallet/${nodeId}`,
						{
							method: "GET",
							headers: {
								"Content-Type": "application/json",
							},
						}
					);

					// Parse the response
					const data = await response.json();
					console.log(data);
					setWalletData(data);
					setShowOverlay(true);
				})();
			},
			doubleClickNode: (event) => {
				(async () => {
					const nodeId = event.node;
					console.log(`Node: ${nodeId} double clicked`, event);

					// Send a web request to the backend
					// TODO: Add error handling and loading state and extract this into a function
					const response = await fetch(
						`http://localhost:8000/connected-wallets/${nodeId}`,
						{
							method: "GET",
							headers: {
								"Content-Type": "application/json",
							},
						}
					);

					// Parse the response
					const data = await response.json();
					const connectedWallets: ConnectedWallets = data;

					const graph = sigma.getGraph();
					for (const connection in connectedWallets.inbound_connections) {
						if (!graph.hasNode(connection)) {
							const coords: Coordinates = sigma.viewportToGraph({
								x: Math.random() * 100,
								y: Math.random() * 100,
							});
							graph.addNode(connection, {
								size: 25,
								color: "grey",
								x: coords.x,
								y: coords.y,
							});
						}

						if (!graph.hasEdge(nodeId, connection)) {
							const num_transactions =
								connectedWallets.inbound_connections[connection]
									.num_transactions;
							graph.addEdge(nodeId, connection, {
								size: 3,
								label:
									num_transactions === -1
										? ""
										: `${num_transactions} transactions`,
							});
							// Set the edge type to curved if the nodes are connected in both directions
							if (graph.hasEdge(connection, nodeId)) {
								graph.setEdgeAttribute(nodeId, connection, "type", "curved");
								graph.setEdgeAttribute(nodeId, connection, "type", "curved");
							}
						}
					}
					for (const connection in connectedWallets.outbound_connections) {
						if (!graph.hasNode(connection)) {
							const coords: Coordinates = sigma.viewportToGraph({
								x: Math.random() * 100,
								y: Math.random() * 100,
							});
							graph.addNode(connection, {
								size: 25,
								color: "grey",
								x: coords.x,
								y: coords.y,
							});
						}

						if (!graph.hasEdge(connection, nodeId)) {
							const num_transactions =
								connectedWallets.outbound_connections[connection]
									.num_transactions;
							graph.addEdge(connection, nodeId, {
								size: 3,
								label:
									num_transactions === -1
										? ""
										: `${num_transactions} transactions`,
							});
							// Set the edge type to curved if the nodes are connected in both directions
							if (graph.hasEdge(nodeId, connection)) {
								graph.setEdgeAttribute(nodeId, connection, "type", "curved");
								graph.setEdgeAttribute(nodeId, connection, "type", "curved");
							}
						}
					}
				})();
			},
			enterNode: (event) => {
				const nodeId = event.node;
				console.log(`Node: ${nodeId} entered`, event);
				const graph = sigma.getGraph();
				graph.setNodeAttribute(nodeId, "label", nodeId);
			},
			leaveNode: (event) => {
				const nodeId = event.node;
				console.log(`Node: ${nodeId} left`, event);
				const graph = sigma.getGraph();
				graph.setNodeAttribute(nodeId, "label", "");
			},
		});
	}, [registerEvents, sigma, setWalletData, setShowOverlay]);
	return null;
};

const GraphWrapper = () => {
	// State to manage the node data for the overlay
	const [walletData, setWalletData] = useState<WalletData | null>(null);
	const [showOverlay, setShowOverlay] = useState(false);
	const [showModal, setShowModal] = useState(true);
	const [darkMode, setDarkMode] = useState(false);

	const handleCloseModal = () => setShowModal(false);

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
			<ControlsContainer
				position={"bottom-left"}
				className="graph-controls-container"
			>
				<ZoomControl />
				<FullScreenControl />
				<Button
					variant="dark"
					className="px-3 w-100 border-0 btn btn-dark"
					style={{ borderRadius: "0", backgroundColor: "#1a1a1a" }}
					onClick={() => {
						setDarkMode(!darkMode);
						document.body.setAttribute(
							"data-bs-theme",
							darkMode ? "light" : "dark"
						);
					}} // TODO: Fix styling to match other controls
				>
					{darkMode ? <SunFill /> : <MoonFill />}
				</Button>
			</ControlsContainer>
			<GraphEvents
				setWalletData={setWalletData}
				setShowOverlay={setShowOverlay}
			/>
			<ForceAtlasLayout />
			<WalletInfoOverlay
				walletData={walletData}
				show={showOverlay}
				setShow={setShowOverlay}
			/>
			<InitialModal show={showModal} handleClose={handleCloseModal} />
		</SigmaContainer>
	);
};

export default GraphWrapper;
