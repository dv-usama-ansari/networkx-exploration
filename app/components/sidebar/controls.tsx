"use client";

import { GraphConfig } from "@/app/types";
import {
  Accordion,
  Badge,
  Button,
  CheckIcon,
  Combobox,
  Divider,
  Group,
  Pill,
  PillsInput,
  PillsInputProps,
  ScrollArea,
  SegmentedControl,
  Stack,
  Switch,
  Text,
  useCombobox,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import * as React from "react";

function SearchableMultiSelect({
  items,
  value,
  setValue,
  ...props
}: {
  items: string[];
  value: string[];
  setValue: React.Dispatch<React.SetStateAction<string[]>>;
} & PillsInputProps) {
  const combobox = useCombobox({
    onDropdownClose: () => combobox.resetSelectedOption(),
    onDropdownOpen: () => combobox.updateSelectedOptionIndex("active"),
  });

  const [search, setSearch] = React.useState("");

  const handleValueSelect = (val: string) => {
    return setValue((current) =>
      current.includes(val)
        ? current.filter((v) => v !== val)
        : [...current, val]
    );
  };

  const handleValueRemove = (val: string) =>
    setValue((current) => current.filter((v) => v !== val));

  const values = value.map((item) => (
    <Pill key={item} withRemoveButton onRemove={() => handleValueRemove(item)}>
      {item}
    </Pill>
  ));

  const options = items
    .filter((item) => item.toLowerCase().includes(search.trim().toLowerCase()))
    .map((item) => (
      <Combobox.Option value={item} key={item} active={value.includes(item)}>
        <Group gap="sm">
          {value.includes(item) ? <CheckIcon size={12} /> : null}
          <span>{item}</span>
        </Group>
      </Combobox.Option>
    ));

  return (
    <Combobox store={combobox} onOptionSubmit={handleValueSelect} withinPortal>
      <Combobox.DropdownTarget>
        <PillsInput onClick={() => combobox.openDropdown()} {...props}>
          <Pill.Group>
            {values}

            <Combobox.EventsTarget>
              <PillsInput.Field
                onFocus={() => combobox.openDropdown()}
                onBlur={() => combobox.closeDropdown()}
                value={search}
                placeholder="Search values"
                onChange={(event) => {
                  combobox.updateSelectedOptionIndex();
                  setSearch(event.currentTarget.value);
                }}
                onKeyDown={(event) => {
                  if (
                    event.key === "Backspace" &&
                    search.length === 0 &&
                    value.length > 0
                  ) {
                    event.preventDefault();
                    handleValueRemove(value[value.length - 1]);
                  }
                }}
              />
            </Combobox.EventsTarget>
          </Pill.Group>
        </PillsInput>
      </Combobox.DropdownTarget>

      <Combobox.Dropdown>
        <Combobox.Header>
          <Button
            leftSection={items.length === value.length ? <CheckIcon /> : null}
            onClick={() => {
              setValue(items);
            }}
          >
            Select all
          </Button>
        </Combobox.Header>
        <Combobox.Options>
          <ScrollArea.Autosize mah={200}>
            {options.length > 0 ? (
              options
            ) : (
              <Combobox.Empty>Nothing found...</Combobox.Empty>
            )}
          </ScrollArea.Autosize>
        </Combobox.Options>
      </Combobox.Dropdown>
    </Combobox>
  );
}

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
  const [
    withIdtypeNodes,
    { toggle: toggleIdtypeNodes, open: enableWithIdtypeNodes },
  ] = useDisclosure(true);
  const [
    withIntermediateEdges,
    { toggle: toggleIntermediateEdges, open: enableWithIntermediateEdges },
  ] = useDisclosure(true);
  const [
    removeIsolatedNodes,
    { toggle: toggleRemoveIsolatedNodes, close: disableRemoveIsolatedNodes },
  ] = useDisclosure(false);
  const [fileList, setFileList] = React.useState<string[]>([]);
  const [selectedFileList, setSelectedFileList] = React.useState<string[]>([]);
  const [loadedLandscapeList, setLoadedLandscapeList] = React.useState<
    string[]
  >([]);

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

  const addLandscapes = React.useCallback(async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/graph/add_landscapes",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(selectedFileList),
        }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
    } catch (error) {
      console.error("Error adding landscapes:", error);
    }
  }, [selectedFileList, setGraph]);

  React.useEffect(() => {
    const fetchFileList = async () => {
      try {
        const response = await fetch(
          "http://localhost:8000/api/graph/get_available_landscapes",
          { method: "GET" }
        );
        const data: string[] = await response.json();
        setFileList(data);
      } catch (error) {
        console.error("Error fetching available landscapes:", error);
      }
    };

    fetchFileList();
  }, []);

  React.useEffect(() => {
    const fetchLoadedLandscapeList = async () => {
      try {
        const response = await fetch(
          "http://localhost:8000/api/graph/get_loaded_landscapes",
          { method: "GET" }
        );
        const data: string[] = await response.json();
        setLoadedLandscapeList(data);
      } catch (error) {
        console.error("Error fetching loaded landscapes:", error);
      }
    };

    fetchLoadedLandscapeList();
  }, [graph?.nodes.length]);

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
          <Accordion.Control>
            <Group justify="space-between">
              <Text>Landscape controls</Text>
              <Badge color="blue" variant="light">
                {loadedLandscapeList.length}
              </Badge>
            </Group>
          </Accordion.Control>
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

                <SearchableMultiSelect
                  items={fileList}
                  value={selectedFileList}
                  setValue={setSelectedFileList}
                />
                <Button
                  onClick={addLandscapes}
                  disabled={selectedFileList.length === 0}
                >
                  Add selected landscapes
                </Button>
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
      <Button
        onClick={() => {
          setGraphMode("2d");
          fetchResetGraph();
          setSelectedFileList([]);
          enableWithIdtypeNodes();
          enableWithIntermediateEdges();
          disableRemoveIsolatedNodes();
        }}
        disabled={!graph}
        color="red"
      >
        Reset graph
      </Button>
    </Stack>
  );
}
