"use client";

import { GraphConfig } from "@/app/types";
import { Button, Divider, Stack, Switch } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import * as React from "react";

export function Controls({
  graph,
  setGraph,
}: {
  graph: GraphConfig | null;
  setGraph: React.Dispatch<React.SetStateAction<GraphConfig | null>>;
}) {
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
        "http://localhost:8000/api/graph/get_graph?with_idtype_nodes=" +
          hideIdtypeNodes,
        { method: "GET" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, [hideIdtypeNodes, setGraph]);

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
  );
}
