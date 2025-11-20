import { Box, Fieldset } from "@mantine/core";
import { Controls } from "./controls";
import { Query } from "./query";
import { GraphConfig } from "@/app/types";

export function Sidebar({
  graph,
  setGraph,
}: {
  graph: GraphConfig | null;
  setGraph: React.Dispatch<React.SetStateAction<GraphConfig | null>>;
}) {
  return (
    <Box h="100%" style={{ display: "grid", gridTemplateRows: "1fr 1fr" }}>
      <Controls graph={graph} setGraph={setGraph} />
      {graph ? (
        <Fieldset legend="Fetch relations for node" miw={320}>
          <Query graph={graph} setGraph={setGraph} />
        </Fieldset>
      ) : null}
    </Box>
  );
}
