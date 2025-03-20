import { openDB, IDBPDatabase } from "idb";
import { WalletData } from "../types/WalletData";

const DB_NAME = "bitcaml-data";

export class WalletDataCache {
	private db: IDBPDatabase | null = null;

	public async init() {
		console.log("Cache initialized");
		this.db = await openDB(DB_NAME, 1, {
			upgrade(db) {
				db.createObjectStore("session-details");
				db.createObjectStore("wallet-data");
			},
		});
	}

	public async initWithInitialWalletAddress(initialWalletAddress: string) {
		if (!initialWalletAddress) {
			throw new Error("Wallet address is empty");
		}

		if (!this.db) {
			await this.init();
		}

		const initialWalletAddressFromDB = await this.getInitialWalletAddress();
		if (initialWalletAddressFromDB != initialWalletAddress) {
			console.log(
				`New wallet address: ${initialWalletAddress} does not match the old wallet address: ${initialWalletAddressFromDB}, clearing the cache`
			);
			await this.db!.clear("wallet-data");
			await this.setInitialWalletAddress(initialWalletAddress);
		}
	}

	public async getInitialWalletAddress(): Promise<string | undefined> {
		if (!this.db) {
			throw new Error("Cache is not initialized");
		}
		console.log("Getting initial wallet address from cache");
		return this.db.get("session-details", "initial-wallet-address");
	}

	public async setInitialWalletAddress(walletAddress: string) {
		if (!walletAddress) {
			throw new Error("Wallet address is empty");
		}
		if (!this.db) {
			throw new Error("Cache is not initialized");
		}
		await this.db.put(
			"session-details",
			walletAddress,
			"initial-wallet-address"
		);
	}

	public async getAllWalletData(): Promise<WalletData[]> {
		if (!this.db) {
			throw new Error("Cache is not initialized");
		}
		return this.db.getAll("wallet-data");
	}

	public async getCachedWalletData(
		walletAddress: string
	): Promise<WalletData | undefined> {
		if (!walletAddress) {
			throw new Error("Wallet address is empty");
		}
		if (!this.db) {
			throw new Error("Cache is not initialized");
		}
		return this.db.get("wallet-data", walletAddress);
	}

	public async cacheWalletData(walletAddress: string, data: WalletData) {
		if (!walletAddress) {
			throw new Error("Wallet address is empty");
		}
		if (!this.db) {
			throw new Error("Cache is not initialized");
		}
		console.log("Caching wallet data for", walletAddress);
		await this.db.put("wallet-data", data, walletAddress);
	}
}
