import { useState } from "react";
import {
	Button,
	Form,
	Modal,
	Spinner,
	Toast,
	ToastContainer,
} from "react-bootstrap";
import logo from "../assets/logo.svg"; // Import the SVG file
import { useSigma } from "@react-sigma/core";
import Config from "../config/Config"; // Import the configuration class
import { XCircleFill } from "react-bootstrap-icons";

const InitialModal = ({
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

	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();
		setLoading(true);

		// TODO: Extract this code into a backend client class
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 seconds timeout

		try {
			// Send a web request to the backend
			const response = await fetch(
				`${Config.getBackendBaseUrl()}/wallet/${walletAddress}`,
				{
					method: "GET",
					headers: {
						"Content-Type": "application/json",
					},
					signal: controller.signal,
				}
			);

			// Parse the response
			const data = await response.json();
			console.log(data);

			const graph = sigma.getGraph();
			graph.addNode(walletAddress, {
				size: 25,
				color: "grey",
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
			// Clear the error message after 3 seconds
			setTimeout(() => {
				setShowToast(false);
				setError("");
			}, 3000);
		} finally {
			clearTimeout(timeoutId);
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
			<ToastContainer position="bottom-center">
				<Toast
					show={showToast}
					onClose={() => setShowToast(false)}
					bg="danger"
					delay={3000}
					autohide
				>
					<Toast.Body className="text-white d-flex align-items-center">
						<XCircleFill className="me-2" />
						<strong className="me-1">Error Sending Request: </strong>
						{error}
					</Toast.Body>
				</Toast>
			</ToastContainer>
		</>
	);
};

export default InitialModal;
