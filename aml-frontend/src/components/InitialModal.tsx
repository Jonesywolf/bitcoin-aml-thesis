import { useState } from "react";
import { Button, Form, Modal, Spinner } from "react-bootstrap";
import logo from "../assets/logo.svg"; // Import the SVG file
import { useSigma } from "@react-sigma/core";

const InitialModal = ({
	show,
	handleClose,
}: {
	show: boolean;
	handleClose: () => void;
}) => {
	const [walletAddress, setWalletAddress] = useState("");
	const [loading, setLoading] = useState(false);
	const sigma = useSigma();

	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();
		setLoading(true);

		// Send a web request to the backend
		const response = await fetch(
			`http://localhost:8000/wallet/${walletAddress}`,
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

		const graph = sigma.getGraph();

		graph.addNode(walletAddress, {
			size: 25,
			color: "grey",
			x: 0,
			y: 0,
		});

		handleClose();
		setLoading(false);
	};

	return (
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
						<Form.Label>Wallet Address</Form.Label>
						<Form.Control
							type="text"
							placeholder="Enter wallet address"
							value={walletAddress}
							onChange={(e) => setWalletAddress(e.target.value)}
							required
						/>
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
	);
};

export default InitialModal;
