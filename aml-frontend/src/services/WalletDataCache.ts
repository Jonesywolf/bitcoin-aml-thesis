import { openDB, IDBPDatabase } from "idb";
import { WalletData } from "../types/WalletData";

const DB_NAME = "bitcaml-data";
// TODO: Store the graph data in the cache
// TODO: Update the cache using a background service fed by SSRs from the backend

export class WalletDataCache {
	private static db: IDBPDatabase;

	public static async init() {
		WalletDataCache.db = await openDB(DB_NAME, 1, {
			upgrade(db) {
				db.createObjectStore("session-details");
				db.createObjectStore("wallet-data");
			},
		});
	}

	public static async initWithInitialWalletAddress(
		initialWalletAddress: string
	) {
		if (!initialWalletAddress) {
			throw new Error("Wallet address is empty");
		}

		if (!WalletDataCache.db) {
			await WalletDataCache.init();
		}

		const initialWalletAddressFromDB = await WalletDataCache.db.get(
			"session-details",
			"initial-wallet-address"
		);
		if (initialWalletAddressFromDB != initialWalletAddress) {
			console.log(
				`New wallet address: ${initialWalletAddress} does not match the old wallet address: ${initialWalletAddressFromDB}, clearing the cache`
			);
			await WalletDataCache.db.clear("wallet-data");
			await WalletDataCache.db.put(
				"session-details",
				"initial-wallet-address",
				initialWalletAddress
			);
		}
	}

	public static async getInitialWalletAddress(): Promise<string | undefined> {
		if (!WalletDataCache.db) {
			throw new Error("Cache is not initialized");
		}
		return WalletDataCache.db.get("session-details", "initial-wallet-address");
	}

	public static async getCachedWalletData(
		walletAddress: string
	): Promise<WalletData | undefined> {
		if (!walletAddress) {
			throw new Error("Wallet address is empty");
		}
		if (!WalletDataCache.db) {
			throw new Error("Cache is not initialized");
		}
		return WalletDataCache.db.get("wallet-data", walletAddress);
	}

	public static async cacheWalletData(walletAddress: string, data: WalletData) {
		if (!walletAddress) {
			throw new Error("Wallet address is empty");
		}
		if (!WalletDataCache.db) {
			throw new Error("Cache is not initialized");
		}
		await WalletDataCache.db.put("wallet-data", data, walletAddress);
	}
}
