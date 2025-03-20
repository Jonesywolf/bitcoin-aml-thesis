import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import GraphWrapper from "./components/GraphWrapper";
import { useState, useEffect } from "react";
import { GlobalContext } from "./contexts/GlobalContext";
import { WalletDataCache } from "./services/WalletDataCache";
import { Spinner } from "react-bootstrap";

function App() {
	const [globalState, setGlobalState] = useState({
		walletCache: new WalletDataCache(),
	});
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const initializeWalletCache = async () => {
			// Assume some async initialization if needed
			await globalState.walletCache.init();
			setLoading(false);
		};

		initializeWalletCache();
	}, [globalState]);

	if (loading) {
		return (
			<div className="d-flex justify-content-center align-items-center vh-100">
				<Spinner animation="border" role="status"></Spinner>
			</div>
		);
	}

	return (
		<GlobalContext.Provider value={{ globalState, setGlobalState }}>
			<GraphWrapper />
		</GlobalContext.Provider>
	);
}

export default App;
