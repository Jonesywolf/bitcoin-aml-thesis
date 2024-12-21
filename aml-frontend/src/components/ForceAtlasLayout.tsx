import { useWorkerLayoutForce } from "@react-sigma/layout-force";
import { useEffect } from "react";

const ForceAtlasLayout = () => {
	const { start, kill } = useWorkerLayoutForce({
		settings: {
			maxMove: 1,
		},
	});

	useEffect(() => {
		// Start Force Atlas Layout
		start();

		// Kill Force Atlas Layout on unmount
		return () => {
			kill();
		};
	}, [start, kill]);

	return null;
};

export default ForceAtlasLayout;
