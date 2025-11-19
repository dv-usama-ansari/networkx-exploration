"use client";

import {
  ActionIcon,
  Box,
  Button,
  CloseButton,
  Code,
  Divider,
  Fieldset,
  ScrollArea,
  Select,
  Stack,
  Switch,
  Text,
} from "@mantine/core";
import { useDisclosure, useElementSize, useViewportSize } from "@mantine/hooks";
import * as React from "react";
import { GraphComponent, GraphConfig } from "./components/graph";

export default function Home() {
  const [graph, setGraph] = React.useState<GraphConfig | null>(null);
  const [graphNode, setGraphNode] = React.useState<string | null>(null);
  const [relations, setRelations] = React.useState<unknown[] | null>(null);
  const { height, width } = useViewportSize();
  const { ref: sidebarRef, width: sidebarWidth } = useElementSize();
  const [hideIdtypeNodes, { toggle: toggleIdtypeNodes }] = useDisclosure(false);

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

  const fetchGraphWithIdtypeNodes = React.useCallback(async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/graph/get_graph?with_idtype_nodes=" +
          hideIdtypeNodes,
        { method: "GET" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, [hideIdtypeNodes]);

  const addTestDb1 = React.useCallback(async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/graph/add_test_db1",
        { method: "POST" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
    } catch (error) {
      console.error("Error adding test db:", error);
    }
  }, []);

  const addTestDb2 = React.useCallback(async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/graph/add_test_db2",
        { method: "POST" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
    } catch (error) {
      console.error("Error adding test db:", error);
    }
  }, []);

  const addOrdinoPublic = React.useCallback(async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/graph/add_ordino_public",
        { method: "POST" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
    } catch (error) {
      console.error("Error adding test db:", error);
    }
  }, []);

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
              <GraphComponent
                graph={graph}
                height={height - 72}
                width={width - (sidebarWidth ?? 0) - 96}
              />
            </Fieldset>
          ) : null}
        </Box>
      </Fieldset>
      <Fieldset legend="Controls" p="md" ref={sidebarRef}>
        <Box h="100%" style={{ display: "grid", gridTemplateRows: "1fr 1fr" }}>
          <Stack>
            <Button onClick={fetchInitialGraph}>Load visyn_kb graph</Button>
            <Button onClick={fetchIdtypeRelations} disabled={!graph}>
              Load visyn_kb idtype relations
            </Button>
            <Switch
              checked={hideIdtypeNodes}
              onChange={() => {
                toggleIdtypeNodes();
                fetchGraphWithIdtypeNodes();
              }}
              label="Hide idtype nodes"
              disabled={!graph}
            />
            <Button onClick={fetchOneToNRelations} disabled={!graph}>
              Load visyn_kb 1-n relations
            </Button>
            <Button onClick={fetchOrdinoDrilldownRelations} disabled={!graph}>
              Load visyn_kb drilldown relations
            </Button>
            <Divider />
            <Button onClick={addTestDb1}>Add test db 1</Button>
            <Button onClick={addTestDb2}>Add test db 2</Button>
            <Button onClick={addOrdinoPublic}>Add ordino public</Button>
            <Divider />
            <Button onClick={fetchResetGraph} disabled={!graph} color="red">
              Reset graph
            </Button>
          </Stack>
          {graph ? (
            <Fieldset legend="Fetch relations for node" miw={320}>
              <Stack>
                <Select
                  data={graph.nodes?.map((n) => n.id)}
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
                    Get relations
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
            </Fieldset>
          ) : null}
        </Box>
      </Fieldset>
    </Box>
  );
}
