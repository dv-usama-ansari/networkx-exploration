"use client";

import { GraphConfig } from "@/app/types";
import { Box, Divider, SegmentedControl, Stack } from "@mantine/core";
import { Controls } from "./controls";
import { Query } from "./query";

export function Sidebar({
  graph,
  setGraph,
  graphMode,
  setGraphMode,
}: {
  graph: GraphConfig | null;
  setGraph: React.Dispatch<React.SetStateAction<GraphConfig | null>>;
  graphMode: "2d" | "3d";
  setGraphMode: React.Dispatch<React.SetStateAction<"2d" | "3d">>;
}) {
  return (
    <Box
      h="100%"
      style={{ display: "grid", gridTemplateRows: "auto 1fr 1fr", gap: "1rem" }}
    >
      <Controls
        graph={graph}
        setGraph={setGraph}
        graphMode={graphMode}
        setGraphMode={setGraphMode}
      />
      {graph ? (
        <Stack>
          <Divider />
          <Query graph={graph} setGraph={setGraph} />
        </Stack>
      ) : null}
    </Box>
  );
}
