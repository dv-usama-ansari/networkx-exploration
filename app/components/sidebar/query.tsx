import { GraphConfig } from "@/app/types";
import {
  ActionIcon,
  Box,
  Button,
  CloseButton,
  Code,
  Fieldset,
  ScrollArea,
  Select,
  Stack,
} from "@mantine/core";
import * as React from "react";

export function Query({
  graph,
  setGraph,
}: {
  graph: GraphConfig | null;
  setGraph: React.Dispatch<React.SetStateAction<GraphConfig | null>>;
}) {
  const [relations, setRelations] = React.useState<unknown[] | null>(null);
  const [graphNode, setGraphNode] = React.useState<string | null>(null);

  const fetchRelationsForNode = React.useCallback(async () => {
    if (!graphNode) return;
    try {
      const response = await fetch(
        "http://localhost:8000/api/graph/get_relations/" + graphNode
      );
      const data: unknown[] = await response.json();
      setRelations(data);
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, [graphNode]);

  return (
    <Stack>
      <Select
        data={graph?.nodes?.map((n) => n.id)}
        onChange={setGraphNode}
        value={graphNode}
        searchable
        nothingFoundMessage="No options"
        placeholder="Select node"
      />
      <Box
        style={{
          display: "grid",
          gridTemplateColumns: relations ? "1fr auto" : "1fr",
          alignItems: "center",
          gap: "1rem",
        }}
      >
        <Button onClick={fetchRelationsForNode} disabled={!graphNode}>
          Query relations
        </Button>
        {relations ? (
          <ActionIcon
            onClick={() => {
              setRelations(null);
            }}
            variant="subtle"
          >
            <CloseButton />
          </ActionIcon>
        ) : null}
      </Box>
      {relations ? (
        <Fieldset legend="Relations">
          <ScrollArea.Autosize maw={320} mah={400} scrollbars="xy">
            <Code block>{JSON.stringify(relations, null, 2)}</Code>
          </ScrollArea.Autosize>
        </Fieldset>
      ) : null}
    </Stack>
  );
}
