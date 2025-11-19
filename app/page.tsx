"use client";

import { Box, Button, Fieldset, Paper, Stack } from "@mantine/core";
import { useViewportSize } from "@mantine/hooks";
import dynamic from "next/dynamic";
import * as React from "react";
import { GraphComponent, GraphConfig } from "./components/graph";

const ForceGraph = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

export default function Home() {
  const [graph, setGraph] = React.useState<GraphConfig | null>(null);
  const { height, width } = useViewportSize();

  const fetchInitialGraph = React.useCallback(async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/graph/populate_graph",
        { method: "POST" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, []);

  const fetchIdtypeRelations = React.useCallback(async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/graph/populate_idtype_relations",
        { method: "POST" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, []);

  const fetchOneToNRelations = React.useCallback(async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/graph/populate_one_to_n_relations",
        { method: "POST" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, []);

  const fetchOrdinoDrilldownRelations = React.useCallback(async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/graph/populate_ordino_drilldown_relations",
        { method: "POST" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, []);

  const fetchResetGraph = React.useCallback(async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/graph/reset_graph",
        { method: "POST" }
      );
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
              <GraphComponent
                graph={graph}
                height={height - 69}
                width={width - 411}
              />
            </Paper>
          ) : null}
        </Box>
      </Fieldset>
      <Fieldset legend="Controls" p="md">
        <Stack>
          <Button onClick={fetchInitialGraph}>Load graph</Button>
          <Button onClick={fetchIdtypeRelations}>Load idtype relations</Button>
          <Button onClick={fetchOneToNRelations}>Load 1-n relations</Button>
          <Button onClick={fetchOrdinoDrilldownRelations}>
            Load ordino drilldown relations
          </Button>
          <Button onClick={fetchResetGraph}>Reset graph</Button>
        </Stack>
      </Fieldset>
    </Box>
  );
}
