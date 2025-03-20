import { useContext, useEffect, useMemo, useRef, useState } from "react";
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
import { getNodeColor, WalletData } from "../types/WalletData";
import WalletInfoOverlay from "./WalletInfoOverlay";
import WalletAddressModal from "./WalletAddressModal";
import { Button } from "react-bootstrap";
import { MoonFill, SunFill } from "react-bootstrap-icons";
import { Coordinates } from "sigma/types";
import { LayoutForceAtlas2Control } from "@react-sigma/layout-forceatlas2";
import BackendService from "../services/BackendService";
import ErrorToast from "./ErrorToast";
import { GlobalContext } from "../contexts/GlobalContext";

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

function randomCoordinatesAroundCenter(center: Coordinates): Coordinates {
	const radius = 10;
	const angle = Math.random() * 2 * Math.PI;
	return {
		x: center.x + radius * Math.cos(angle),
		y: center.y + radius * Math.sin(angle),
	};
}

const GraphEvents = ({
	setWalletData,
	setShowOverlay,
	setError,
	setShowToast,
}: {
	setWalletData: React.Dispatch<React.SetStateAction<WalletData | null>>;
	setShowOverlay: React.Dispatch<React.SetStateAction<boolean>>;
	setError: React.Dispatch<React.SetStateAction<string>>;
	setShowToast: React.Dispatch<React.SetStateAction<boolean>>;
}) => {
	const sigma = useSigma();
	const registerEvents = useRegisterEvents();
	const globalContext = useContext(GlobalContext);
	if (!globalContext) {
		throw new Error("Global context is not defined");
	}
	const { globalState } = globalContext;

	useEffect(() => {
		registerEvents({
			clickNode: (event) => {
				(async () => {
					const nodeId = event.node;
					console.log(`Node: ${nodeId} clicked`, event);

					try {
						const response = await BackendService.fetchWalletDataWithCache(
							nodeId,
							globalState
						);

						// The wallet data is fetched successfully
						setWalletData(response);

						const graph = sigma.getGraph();
						const nodeColor = getNodeColor(response);
						graph.setNodeAttribute(nodeId, "color", nodeColor);

						setShowOverlay(true);
					} catch (error: unknown) {
						if (error instanceof Error && error.name === "AbortError") {
							console.error("Wallet data request timed out");
							setError("Wallet data request timed out");
						} else {
							console.error("Wallet data request failed with", error);
							setError("Wallet data request failed");
						}
						setShowToast(true);
					}
				})();
			},
			doubleClickNode: (event) => {
				(async () => {
					const nodeId = event.node;
					console.log(`Node: ${nodeId} double clicked`, event);

					try {
						const connectedWallets = await BackendService.fetchConnectedWallets(
							nodeId
						);
						const graph = sigma.getGraph();
						const node = graph.getNodeAttributes(nodeId);
						const nodeCoords: Coordinates = {
							x: node.x,
							y: node.y,
						};
						console.log(node.x, node.y);
						for (const connection in connectedWallets.inbound_connections) {
							if (!graph.hasNode(connection)) {
								const coords: Coordinates =
									randomCoordinatesAroundCenter(nodeCoords);
								graph.addNode(connection, {
									size: 10,
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
								const coords: Coordinates =
									randomCoordinatesAroundCenter(nodeCoords);
								graph.addNode(connection, {
									size: 10,
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
					} catch (error: unknown) {
						if (error instanceof Error && error.name === "AbortError") {
							console.error("Connected wallets request timed out");
							setError("Connected wallets request timed out");
						} else {
							console.error("Connected wallets request failed with", error);
							setError("Connected wallets request failed");
						}
						setShowToast(true);
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
	}, [
		registerEvents,
		sigma,
		setWalletData,
		setShowOverlay,
		setError,
		setShowToast,
		globalState,
	]);
	return null;
};

const GraphWrapper = () => {
	// State to manage the node data for the overlay
	const [walletData, setWalletData] = useState<WalletData | null>(null);
	const [showOverlay, setShowOverlay] = useState(false);
	const [showModal, setShowModal] = useState(false);
	const [error, setError] = useState("");
	const [showToast, setShowToast] = useState(false);
	const [darkMode, setDarkMode] = useState(false);

	const handleCloseModal = () => setShowModal(false);

	const globalContext = useContext(GlobalContext);
	if (!globalContext) {
		throw new Error("Global context is not defined");
	}

	const { globalState, setGlobalState } = globalContext;

	useEffect(() => {
		const initializeWalletCache = async () => {
			const initialWalletAddress =
				await globalState.walletCache.getInitialWalletAddress();
			console.log("Initial wallet address", initialWalletAddress);
			if (initialWalletAddress) {
				globalState.walletCache.initWithInitialWalletAddress(
					initialWalletAddress
				);
			} else {
				setShowModal(true);
			}
		};

		initializeWalletCache();
	}, [globalState.walletCache, setGlobalState]);

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
			// TODO: Customize the controls:
			https://sim51.github.io/react-sigma/docs/example/controls#custom-render-for-controls
			<ControlsContainer
				position={"bottom-left"}
				className="graph-controls-container"
			>
				<ZoomControl />
				<FullScreenControl />
				<LayoutForceAtlas2Control
					settings={{
						settings: {
							strongGravityMode: true,
							slowDown: 10,
							scalingRatio: 2,
						},
					}}
				/>
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
				setError={setError}
				setShowToast={setShowToast}
			/>
			<WalletInfoOverlay
				walletData={walletData}
				show={showOverlay}
				setShow={setShowOverlay}
			/>
			<ErrorToast
				showToast={showToast}
				setShowToast={setShowToast}
				errorTitle="Error:"
				error={error}
			/>
			<WalletAddressModal show={showModal} handleClose={handleCloseModal} />
		</SigmaContainer>
	);
};

export default GraphWrapper;
