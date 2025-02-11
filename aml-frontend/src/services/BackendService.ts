import Config from "../config/Config";
import ConnectedWallets from "../types/ConnectedWallets";
import { WalletData } from "../types/WalletData";
import { WalletDataCache } from "./WalletDataCache";

class BackendService {
	static async fetchWalletData(
		walletAddress: string,
		timeout: number = 10000
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

	static async fetchWalletDataWithCache(
		walletAddress: string,
		timeout: number = 10000
	): Promise<WalletData> {
		if (!walletAddress) {
			throw new Error("Wallet address is empty");
		}

		// Check if the wallet data is in the cache
		const cachedData = await WalletDataCache.getCachedWalletData(walletAddress);
		if (cachedData) {
			console.log("Data from cache:", cachedData);
			return cachedData;
		}

		// Fetch the wallet data from the backend
		const data = await this.fetchWalletData(walletAddress, timeout);
		console.log("Data from API:", data);

		// Cache the fetched data
		await WalletDataCache.cacheWalletData(walletAddress, data);

		return data;
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
