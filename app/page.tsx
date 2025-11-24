"use client";

import { Box, Fieldset } from "@mantine/core";
import { useElementSize, useViewportSize } from "@mantine/hooks";
import * as React from "react";
import { Graph2D, Graph3D } from "./components/graph";
import { Sidebar } from "./components/sidebar";
import { GraphConfig } from "./types";

export default function Home() {
  const [graph, setGraph] = React.useState<GraphConfig | null>(null);
  const [graphMode, setGraphMode] = React.useState<"2d" | "3d">("2d");

  const { height, width } = useViewportSize();
  const { ref: sidebarRef, width: sidebarWidth } = useElementSize();

  return (
    <Box
      style={{
        display: "grid",
        gridTemplateColumns: "1fr auto",
        height: "100vh",
        gap: "1rem",
      }}
      p="md"
    >
      <Fieldset legend="Graph">
        <Box style={{ display: "grid", placeContent: "center" }}>
          {graph ? (
            <Fieldset p={0} m={0}>
              {graphMode === "2d" ? (
                <Graph2D
                  graph={graph}
                  height={height - 86}
                  width={width - (sidebarWidth ?? 0) - 100}
                />
              ) : graphMode === "3d" ? (
                <Graph3D
                  graph={graph}
                  height={height - 86}
                  width={width - (sidebarWidth ?? 0) - 100}
                />
              ) : null}
            </Fieldset>
          ) : null}
        </Box>
      </Fieldset>
      <Fieldset legend="Controls" p="md" ref={sidebarRef}>
        <Sidebar
          graph={graph}
          setGraph={setGraph}
          graphMode={graphMode}
          setGraphMode={setGraphMode}
        />
      </Fieldset>
    </Box>
  );
}
