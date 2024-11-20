interface Connection {
	num_transactions: number;
	amount_transacted: number;
}

interface ConnectedWallets {
	wallet_address: string;
	inbound_connections: Record<string, Connection>;
	outbound_connections: Record<string, Connection>;
}

export default ConnectedWallets;
