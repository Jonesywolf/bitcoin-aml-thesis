class Config {
	static getBackendBaseUrl(): string {
		const baseUrl = import.meta.env.VITE_BACKEND_BASE_URL;
		if (!baseUrl) {
			throw new Error(
				"REACT_APP_BACKEND_BASE_URL is not defined in the environment variables"
			);
		}
		return baseUrl;
	}
}

export default Config;
