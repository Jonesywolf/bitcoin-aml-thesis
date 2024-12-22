import { useState } from "react";
import { Button, Form, Modal, Spinner } from "react-bootstrap";
import logo from "../assets/logo.svg"; // Import the SVG file
import { useSigma } from "@react-sigma/core";
import BackendService from "../services/BackendService";
import ErrorToast from "./ErrorToast";

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

		try {
			const response = await BackendService.fetchWalletData(walletAddress);
			console.log(`Class Inference: ${response.class_inference}`);

			const graph = sigma.getGraph();
			graph.addNode(walletAddress, {
				size: 10,
				color: "grey", //  TODO: Change this to a different color based on the AI prediction
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

export default InitialModal;
