import { GraphConfig } from "@/app/types";
import {
  Accordion,
  ActionIcon,
  Box,
  Button,
  Code,
  CopyButton,
  Group,
  ScrollArea,
  Select,
  Stack,
  Text,
  Tooltip,
} from "@mantine/core";
import { IconCheck, IconCopy, IconTrashX } from "@tabler/icons-react";
import * as React from "react";

export function Query({ graph }: { graph: GraphConfig | null }) {
  const [relations, setRelations] = React.useState<unknown[] | null>(null);
  const [graphNode, setGraphNode] = React.useState<string | null>(null);
  const [landscape, setLandscape] = React.useState<Record<
    string,
    unknown
  > | null>(null);

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

  const fetchFlattenedLandscape = React.useCallback(async () => {
    if (!graph) return;
    try {
      const response = await fetch(
        "http://localhost:8000/api/graph/get_flattened_landscape/"
      );
      const data = await response.json();
      setLandscape(data);
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, [graph]);

  return (
    <Accordion
      defaultValue={["relations", "landscape"]}
      w={320}
      multiple
      variant="separated"
      styles={{ content: { padding: 0 } }}
    >
      <Accordion.Item value="relations">
        <Accordion.Control>
          <Group justify="space-between">
            <Text>Query relations</Text>
          </Group>
        </Accordion.Control>
        <Accordion.Panel>
          <Stack px="md" pb="md">
            <Select
              data={graph?.nodes
                ?.filter((n) => (n.data as { type: string })?.type === "entity")
                ?.map((n) => n.id)}
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
                gap: "0.5rem",
              }}
            >
              <Button onClick={fetchRelationsForNode} disabled={!graphNode}>
                Fetch Relations
              </Button>
              {relations ? (
                <ActionIcon
                  onClick={() => {
                    setRelations(null);
                    setGraphNode(null);
                  }}
                  size="lg"
                  variant="light"
                  color="red"
                >
                  <IconTrashX />
                </ActionIcon>
              ) : null}
            </Box>
            {relations ? (
              <Box style={{ position: "relative" }}>
                <Box
                  style={{ position: "absolute", top: 8, right: 8, zIndex: 99 }}
                >
                  <CopyButton value={JSON.stringify(relations, null, 2)}>
                    {({ copied, copy }) => (
                      <Tooltip
                        label={copied ? "Copied" : "Copy"}
                        withArrow
                        position="right"
                      >
                        <ActionIcon
                          color={copied ? "teal" : "gray"}
                          variant="subtle"
                          onClick={copy}
                        >
                          {copied ? (
                            <IconCheck size={16} />
                          ) : (
                            <IconCopy size={16} />
                          )}
                        </ActionIcon>
                      </Tooltip>
                    )}
                  </CopyButton>
                </Box>
                <ScrollArea.Autosize maw={320} mah={400} scrollbars="xy">
                  <Code block>{JSON.stringify(relations, null, 2)}</Code>
                </ScrollArea.Autosize>
              </Box>
            ) : null}
          </Stack>
        </Accordion.Panel>
      </Accordion.Item>
      <Accordion.Item value="landscape">
        <Accordion.Control>
          <Group justify="space-between">
            <Text>Flattened landscape</Text>
          </Group>
        </Accordion.Control>
        <Accordion.Panel>
          <Stack px="md" pb="md">
            <Box
              style={{
                display: "grid",
                gridTemplateColumns: landscape ? "1fr auto" : "1fr",
                alignItems: "center",
                gap: "0.5rem",
              }}
            >
              <Button onClick={fetchFlattenedLandscape} disabled={!graph}>
                Fetch Landscape
              </Button>
              {landscape ? (
                <ActionIcon
                  onClick={() => {
                    setLandscape(null);
                  }}
                  size="lg"
                  variant="light"
                  color="red"
                >
                  <IconTrashX />
                </ActionIcon>
              ) : null}
            </Box>
            {landscape ? (
              <Box style={{ position: "relative" }}>
                <Box
                  style={{ position: "absolute", top: 8, right: 8, zIndex: 99 }}
                >
                  <CopyButton value={JSON.stringify(landscape, null, 2)}>
                    {({ copied, copy }) => (
                      <Tooltip
                        label={copied ? "Copied" : "Copy"}
                        withArrow
                        position="right"
                      >
                        <ActionIcon
                          color={copied ? "teal" : "gray"}
                          variant="subtle"
                          onClick={copy}
                        >
                          {copied ? (
                            <IconCheck size={16} />
                          ) : (
                            <IconCopy size={16} />
                          )}
                        </ActionIcon>
                      </Tooltip>
                    )}
                  </CopyButton>
                </Box>
                <ScrollArea.Autosize maw={320} mah={400} scrollbars="xy">
                  <Code block>{JSON.stringify(landscape, null, 2)}</Code>
                </ScrollArea.Autosize>
              </Box>
            ) : null}
          </Stack>
        </Accordion.Panel>
      </Accordion.Item>
    </Accordion>
  );
}
