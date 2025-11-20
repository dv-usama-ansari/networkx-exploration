"use client";

import { GraphConfig } from "@/app/types";
import {
  Accordion,
  Button,
  Divider,
  ScrollArea,
  SegmentedControl,
  Stack,
  Switch,
  Text,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import * as React from "react";

export function Controls({
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
  const [withIdtypeNodes, { toggle: toggleIdtypeNodes }] = useDisclosure(true);
  const [withIntermediateEdges, { toggle: toggleIntermediateEdges }] =
    useDisclosure(true);
  const [removeIsolatedNodes, { toggle: toggleRemoveIsolatedNodes }] =
    useDisclosure(false);

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
  }, [setGraph]);

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
  }, [setGraph]);

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
  }, [setGraph]);

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
  }, [setGraph]);

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
  }, [setGraph]);

  const fetchGraphWithIdtypeNodes = React.useCallback(async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/graph/get_graph?with_idtype_nodes=${!withIdtypeNodes}&with_intermediate_edges=${withIntermediateEdges}&remove_isolated_nodes=${removeIsolatedNodes}`,
        { method: "GET" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
      toggleIdtypeNodes();
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, [
    withIdtypeNodes,
    withIntermediateEdges,
    removeIsolatedNodes,
    setGraph,
    toggleIdtypeNodes,
  ]);

  const fetchGraphWithIntermediateEdges = React.useCallback(async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/graph/get_graph?with_idtype_nodes=${withIdtypeNodes}&with_intermediate_edges=${!withIntermediateEdges}&remove_isolated_nodes=${removeIsolatedNodes}`,
        { method: "GET" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
      toggleIntermediateEdges();
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, [
    withIdtypeNodes,
    withIntermediateEdges,
    removeIsolatedNodes,
    setGraph,
    toggleIntermediateEdges,
  ]);

  const fetchGraphWithRemoveIsolatedNodes = React.useCallback(async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/graph/get_graph?with_idtype_nodes=${withIdtypeNodes}&with_intermediate_edges=${withIntermediateEdges}&remove_isolated_nodes=${!removeIsolatedNodes}`,
        { method: "GET" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
      toggleRemoveIsolatedNodes();
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, [
    withIdtypeNodes,
    withIntermediateEdges,
    removeIsolatedNodes,
    setGraph,
    toggleRemoveIsolatedNodes,
  ]);

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
  }, [setGraph]);

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
  }, [setGraph]);

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
  }, [setGraph]);

  return (
    <Stack>
      <Accordion
        defaultValue={["landscapes", "graph_controls"]}
        w={320}
        multiple
        variant="separated"
        styles={{ content: { padding: 0 } }}
      >
        <Accordion.Item value="landscapes">
          <Accordion.Control>Landscape controls</Accordion.Control>
          <Accordion.Panel>
            <ScrollArea.Autosize mah={320}>
              <Stack px="md" pb="md">
                <Divider label="visyn_kb landscape" />
                <Button onClick={fetchInitialGraph}>Load visyn_kb graph</Button>
                <Button onClick={fetchIdtypeRelations} disabled={!graph}>
                  Load visyn_kb idtype relations
                </Button>

                <Button onClick={fetchOneToNRelations} disabled={!graph}>
                  Load visyn_kb 1-n relations
                </Button>
                <Button
                  onClick={fetchOrdinoDrilldownRelations}
                  disabled={!graph}
                >
                  Load visyn_kb drilldown relations
                </Button>
                <Divider label="Other landscapes" />
                <Button onClick={addTestDb1}>Add test db 1</Button>
                <Button onClick={addTestDb2}>Add test db 2</Button>
                <Button onClick={addOrdinoPublic}>Add ordino public</Button>
              </Stack>
            </ScrollArea.Autosize>
          </Accordion.Panel>
        </Accordion.Item>
        <Accordion.Item value="graph_controls">
          <Accordion.Control>Graph controls</Accordion.Control>
          <Accordion.Panel>
            <ScrollArea.Autosize mah={200}>
              <Stack px="md" pb="md">
                <Stack>
                  <Text>Graph type</Text>
                  <SegmentedControl
                    data={["2D", "3D"]}
                    value={graphMode.toUpperCase()}
                    onChange={(v) =>
                      setGraphMode(v.toLowerCase() as "2d" | "3d")
                    }
                    disabled={!graph}
                  />
                </Stack>
                <Switch
                  checked={withIdtypeNodes}
                  onChange={fetchGraphWithIdtypeNodes}
                  label="Show idtype nodes"
                  disabled={!graph}
                />
                <Switch
                  checked={withIntermediateEdges}
                  onChange={fetchGraphWithIntermediateEdges}
                  label="Show intermediate edges"
                  description="This setting will only disable intermediate edges for drilldown relations."
                  disabled={!graph}
                />
                <Switch
                  checked={removeIsolatedNodes}
                  onChange={fetchGraphWithRemoveIsolatedNodes}
                  label="Remove isolated nodes"
                  disabled={!graph}
                />
              </Stack>
            </ScrollArea.Autosize>
          </Accordion.Panel>
        </Accordion.Item>
      </Accordion>
      <Button onClick={fetchResetGraph} disabled={!graph} color="red">
        Reset graph
      </Button>
    </Stack>
  );
}
