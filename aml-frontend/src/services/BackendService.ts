import Config from "../config/Config";
import ConnectedWallets from "../types/ConnectedWallets";
import { WalletData } from "../types/WalletData";

class BackendService {
	static async fetchWalletData(
		walletAddress: string,
		timeout: number = 5000
	): Promise<WalletData> {
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), timeout);

		try {
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

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			return data;
		} finally {
			clearTimeout(timeoutId);
		}
	}

	static async fetchConnectedWallets(
		walletAddress: string,
		timeout: number = 5000
	): Promise<ConnectedWallets> {
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), timeout);

		try {
			const response = await fetch(
				`${Config.getBackendBaseUrl()}/connected-wallets/${walletAddress}`,
				{
					method: "GET",
					headers: {
						"Content-Type": "application/json",
					},
					signal: controller.signal,
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			return data;
		} finally {
			clearTimeout(timeoutId);
		}
	}
}

export default BackendService;
