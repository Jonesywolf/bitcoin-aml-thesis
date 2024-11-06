import { useEffect, useRef } from "react";
import { SigmaContainer, useSigma, useRegisterEvents } from "@react-sigma/core";
import Graph from "graphology";
import { useWorkerLayoutForceAtlas2 } from "@react-sigma/layout-forceatlas2";
import { Coordinates } from "sigma/types";

const GraphComponent = () => {
	const sigma = useSigma();
	const containerRef = useRef(null);

	useEffect(() => {
		const graph = new Graph();
		// Add some nodes
		graph.addNode("n1", {
			label: "Ella Fitzgerald: 1917",
			size: 25,
			color: "red",
			x: 0,
			y: 0,
		});
		graph.addNode("n2", {
			label: "Frank Sinatra: 1915",
			size: 25,
			color: "red",
			x: 0,
			y: 0,
		});
		graph.addNode("n3", {
			label: "Billie Holiday: 1915",
			size: 25,
			color: "red",
			x: 0,
			y: 0,
		});
		graph.addNode("n4", {
			label: "Louis Armstrong: 1901",
			size: 25,
			color: "yellow",
			x: 0,
			y: 0,
		});
		graph.addNode("n5", {
			label: "Nina Simone : 1933",
			size: 25,
			color: "orange",
			x: 0,
			y: 0,
		});
		graph.addNode("n6", {
			label: "Nat King Cole: 1919",
			size: 25,
			color: "red",
			x: 10,
			y: 0,
		});
		graph.addNode("n7", {
			label: "Gregory Porter: 1971",
			size: 25,
			color: "teal",
			x: 15,
			y: 15,
		});
		graph.addNode("n8", {
			label: "Sarah Vaughan: 1924",
			size: 25,
			color: "orange",
			x: 60,
			y: 60,
		});
		graph.addNode("n9", {
			label: "Michael Buble: 1975",
			size: 25,
			color: "teal",
			x: 10,
			y: 10,
		});

		graph.addEdge("n1", "n2");
		graph.addEdge("n1", "n3");
		graph.addEdge("n1", "n6");

		graph.addEdge("n2", "n1");
		graph.addEdge("n3", "n1");
		graph.addEdge("n5", "n8");
		graph.addEdge("n7", "n9");

		if (sigma) {
			sigma.setGraph(graph);
			sigma.refresh();
		}
	}, [sigma]);

	return <div ref={containerRef} />;
};

const GraphEvents = () => {
	const sigma = useSigma();
	const registerEvents = useRegisterEvents();

	useEffect(() => {
		registerEvents({
			clickNode: (event) => {
				console.log("Node clicked", event);
				// Add 1-5 nodes connected to the clicked node
				const graph = sigma.getGraph();
				const nodeId = event.node;
				const node = graph.getNodeAttributes(nodeId);
				const coords: Coordinates = sigma.graphToViewport({
					x: node.x,
					y: node.y,
				});

				// Generate random number of nodes
				const numNodes = Math.floor(Math.random() * 5) + 1;
				for (let i = 0; i < numNodes; i++) {
					const id = `n${graph.order + 1}`;
					graph.addNode(id, {
						label: `Node ${id}`,
						size: 25,
						color: "red",
						x: coords.x + Math.random() * 100 - 50,
						y: coords.y + Math.random() * 100 - 50,
					});
					graph.addEdge(id, nodeId);
				}
			},
			clickStage: (event) => {
				console.log("Stage clicked", event);

				const graph = sigma.getGraph();
				const coords: Coordinates = sigma.viewportToGraph({
					x: event.event.x,
					y: event.event.y,
				});
				const id = `n${graph.order + 1}`;

				// Searching the two closest nodes to auto-create an edge to it
				const closestNodes = graph
					.nodes()
					.map((nodeId) => {
						const attrs = graph.getNodeAttributes(nodeId);
						const distance =
							Math.pow(coords.x - attrs.x, 2) + Math.pow(coords.y - attrs.y, 2);
						return { nodeId, distance };
					})
					.sort((a, b) => a.distance - b.distance)
					.slice(0, 2);

				graph.addNode(id, {
					label: `Node ${id}`,
					size: 25,
					color: "red",
					x: coords.x,
					y: coords.y,
				});

				closestNodes.forEach((node) => {
					graph.addEdge(id, node.nodeId);
				});
			},
		});
	}, [registerEvents, sigma]);
	return null;
};

const Fa2 = () => {
	const { start, kill } = useWorkerLayoutForceAtlas2({
		settings: {
			strongGravityMode: true,
		},
	});

	useEffect(() => {
		// start FA2
		start();

		// Kill FA2 on unmount
		return () => {
			kill();
		};
	}, [start, kill]);

	return null;
};

const GraphWrapper = () => {
	return (
		<SigmaContainer>
			<GraphComponent />
			<GraphEvents />
			<Fa2 />
		</SigmaContainer>
	);
};

export default GraphWrapper;
