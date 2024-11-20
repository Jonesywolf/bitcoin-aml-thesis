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
				setWalletData(data);
				setShowOverlay(true);
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
			<InitialModal
				show={showModal}
				handleClose={handleCloseModal}
				setWalletData={setWalletData}
				setShowOverlay={setShowOverlay}
			/>
		</SigmaContainer>
	);
};

export default GraphWrapper;
