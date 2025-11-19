"use client";

import { Box, Button, Fieldset, Paper, Stack } from "@mantine/core";
import { useViewportSize } from "@mantine/hooks";
import dynamic from "next/dynamic";
import * as React from "react";

const ForceGraph = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

type GraphConfig = {
  directed: boolean;
  multigraph: boolean;
  graph: unknown;
  nodes: {
    id: string;
    data: unknown;
  }[];
  links: {
    source: string;
    target: string;
    data: unknown;
  }[];
};

export default function Home() {
  const [graph, setGraph] = React.useState<GraphConfig | null>(null);
  const { height, width } = useViewportSize();

  const fetchGraph = React.useCallback(async () => {
    try {
      const response = await fetch("http://localhost:8000/api/graph/json");
      const data: GraphConfig = await response.json();
      setGraph(data);
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, []);

  return (
    <Box
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 320px",
        height: "100vh",
        gap: "1rem",
      }}
      p="md"
    >
      <Fieldset legend="Graph">
        <Box style={{ display: "grid", placeContent: "center" }}>
          {graph ? (
            <Paper shadow="md">
              <ForceGraph
                height={height - 69}
                width={width - 411}
                graphData={{ nodes: graph.nodes, links: graph.links }}
                nodeLabel={(n) => n.id!}
                nodeColor={(n) =>
                  n.data?.type === "entity"
                    ? "orange"
                    : n.data?.type === "idtype"
                    ? "green"
                    : n.data?.type === "upload"
                    ? "red"
                    : "gray"
                }
                // nodeRelSize={8}
                linkLabel={(l) => `${JSON.stringify(l.data, null, 2)}`}
                linkColor={(l) =>
                  l.data.type === "idtype-mapping"
                    ? "green"
                    : l.data.type === "1-n"
                    ? "orange"
                    : l.data.type === "n-1"
                    ? "red"
                    : l.data.type === "ordino-drilldown"
                    ? "blue"
                    : "gray"
                }
                linkDirectionalArrowLength={3.5}
                linkDirectionalArrowRelPos={1}
                linkCurvature={0.15}
                // dagMode="bu"
                nodeCanvasObject={(node, ctx, globalScale) => {
                  const label = node.id;
                  const fontSize = 12 / globalScale;
                  ctx.font = `${fontSize}px Sans-Serif`;

                  ctx.fillStyle =
                    node.data?.type === "entity"
                      ? "orange"
                      : node.data?.type === "idtype"
                      ? "green"
                      : node.data?.type === "upload"
                      ? "red"
                      : "gray";

                  ctx.textAlign = "center";
                  ctx.textBaseline = "middle";

                  if (
                    node.data?.type !== "entity" &&
                    node.data?.type !== "idtype" &&
                    node.data?.type !== "upload"
                  ) {
                    ctx.fillText(label, node.x, node.y);
                    const textWidth = ctx.measureText(label).width;
                    ctx.beginPath();
                    ctx.moveTo(node.x - textWidth / 2, node.y);
                    ctx.lineTo(node.x + textWidth / 2, node.y);
                    ctx.strokeStyle = "gray";
                    ctx.lineWidth = 2 / globalScale;
                    ctx.stroke();
                  }
                  ctx.fillText(label, node.x, node.y);
                }}
                onNodeDragEnd={(node) => {
                  node.fx = node.x;
                  node.fy = node.y;
                  node.fz = node.z;
                }}
              />
            </Paper>
          ) : null}
        </Box>
      </Fieldset>
      <Fieldset legend="Controls" p="md">
        <Stack>
          <Button onClick={fetchGraph}>Fetch graph</Button>
        </Stack>
      </Fieldset>
    </Box>
  );
}
