"use client";

import { GraphConfig } from "@/app/types";
import { Box, Divider, Stack } from "@mantine/core";
import { Controls } from "./controls";
import { Query } from "./query";

export function Sidebar({
  graph,
  setGraph,
}: {
  graph: GraphConfig | null;
  setGraph: React.Dispatch<React.SetStateAction<GraphConfig | null>>;
}) {
  return (
    <Box
      h="100%"
      style={{ display: "grid", gridTemplateRows: "1fr 1fr", gap: "1rem" }}
    >
      <Controls graph={graph} setGraph={setGraph} />
      {graph ? (
        <Stack>
          <Divider />
          <Query graph={graph} setGraph={setGraph} />
        </Stack>
      ) : null}
    </Box>
  );
}
