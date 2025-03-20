import { useContext, useEffect, useState } from "react";
import { Button, Form, Modal, Spinner } from "react-bootstrap";
import logo from "../assets/logo.svg"; // Import the SVG file
import { useSigma } from "@react-sigma/core";
import BackendService from "../services/BackendService";
import ErrorToast from "./ErrorToast";
import { getNodeColor } from "../types/WalletData";
import { GlobalContext } from "../contexts/GlobalContext";

const WalletAddressModal = ({
	show,
	handleClose,
}: {
	show: boolean;
	handleClose: () => void;
}) => {
	const [walletAddress, setWalletAddress] = useState("");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [showToast, setShowToast] = useState(false);
	const sigma = useSigma();
	const [initFromCache, setInitFromCache] = useState(false);

	const globalContext = useContext(GlobalContext);
	if (!globalContext) {
		throw new Error("Global context is not defined");
	}
	const { globalState } = globalContext;

	useEffect(() => {
		const fetchInitialWalletAddress = async () => {
			if (!initFromCache) {
				const initialWalletAddress =
					await globalState.walletCache.getInitialWalletAddress();
				if (initialWalletAddress) {
					const allWalletData =
						await globalState.walletCache.getAllWalletData();
					for (const walletData of allWalletData) {
						console.log("Adding node to graph: ", walletData.address);
						const nodeColor = getNodeColor(walletData);
						const graph = sigma.getGraph();
						graph.addNode(walletData.address, {
							size: 10,
							color: nodeColor,
							x: 0,
							y: 0,
						});
					}
				}
				setInitFromCache(true);
			}
		};
		if (!show) {
			fetchInitialWalletAddress();
		}
	}, [globalState, show, initFromCache, sigma]);

	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();
		setLoading(true);

		try {
			// Set up the cache
			globalState.walletCache.initWithInitialWalletAddress(walletAddress);

			const response = await BackendService.fetchWalletDataWithCache(
				walletAddress,
				globalState
			);

			const nodeColor = getNodeColor(response);

			const graph = sigma.getGraph();
			graph.addNode(walletAddress, {
				size: 10,
				color: nodeColor,
				x: 0,
				y: 0,
			});

			handleClose();
		} catch (error: unknown) {
			if (error instanceof Error && error.name === "AbortError") {
				console.error("Request timed out");
				setError("Request timed out");
			} else {
				console.error("Request failed with", error);
				setError("Request failed");
			}
			setShowToast(true);
		} finally {
			setLoading(false);
		}
	};

	return (
		<>
			<Modal show={show} onHide={handleClose} backdrop="static" centered>
				<img
					src={logo}
					alt="Logo"
					style={{ height: "256px", marginTop: "10px" }}
				/>
				<Modal.Header className="d-flex flex-column align-items-center">
					<h1>BitCaml</h1>
					<h5>The Bitcoin Anti-Money Laundering Tool</h5>
				</Modal.Header>
				<Modal.Body>
					<Form onSubmit={handleSubmit}>
						<Form.Group controlId="walletAddress">
							<Form.Control
								type="text"
								placeholder="Enter Wallet Address"
								value={walletAddress}
								onChange={(e) => setWalletAddress(e.target.value)}
								required
							/>
							<Form.Text className="text-muted">
								Try: bc1qa5wkgaew2dkv56kfvj49j0av5nml45x9ek9hz6
							</Form.Text>
						</Form.Group>
						<Button
							variant="primary"
							type="submit"
							className="mt-3"
							disabled={loading}
						>
							{loading ? (
								<>
									<Spinner
										as="span"
										animation="border"
										size="sm"
										aria-hidden="true"
										className="me-2"
									/>
									<output>Loading...</output>
								</>
							) : (
								"Submit"
							)}
						</Button>
					</Form>
				</Modal.Body>
			</Modal>
			<ErrorToast
				showToast={showToast}
				setShowToast={setShowToast}
				errorTitle="Error Sending Request:"
				error={error}
			/>
		</>
	);
};

export default WalletAddressModal;
