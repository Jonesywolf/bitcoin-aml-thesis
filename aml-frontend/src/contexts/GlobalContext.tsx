import { createContext, Dispatch, SetStateAction } from "react";
import { WalletDataCache } from "../services/WalletDataCache";

export interface GlobalState {
	walletCache: WalletDataCache;
}

interface GlobalContextProps {
	globalState: GlobalState;
	setGlobalState: Dispatch<SetStateAction<GlobalState>>;
}

export const GlobalContext = createContext<GlobalContextProps | null>(null);
