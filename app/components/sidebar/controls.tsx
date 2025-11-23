"use client";

import { GraphConfig } from "@/app/types";
import {
  Accordion,
  ActionIcon,
  Badge,
  Box,
  Button,
  CheckIcon,
  Combobox,
  Divider,
  Group,
  HoverCard,
  Modal,
  Pill,
  PillsInput,
  PillsInputProps,
  ScrollArea,
  SegmentedControl,
  Stack,
  Switch,
  Text,
  Textarea,
  TextInput,
  useCombobox,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useDisclosure } from "@mantine/hooks";
import { IconTrash } from "@tabler/icons-react";
import * as React from "react";

function SearchableMultiSelect({
  items,
  value,
  setValue,
  addLandscapes,
  ...props
}: {
  items: string[];
  value: string[];
  setValue: React.Dispatch<React.SetStateAction<string[]>>;
  addLandscapes: () => void;
} & PillsInputProps) {
  const combobox = useCombobox({
    onDropdownClose: () => combobox.resetSelectedOption(),
    onDropdownOpen: () => combobox.updateSelectedOptionIndex("active"),
  });

  const [search, setSearch] = React.useState("");

  const handleValueSelect = React.useCallback(
    (val: string) => {
      setValue((current) =>
        current.includes(val)
          ? current.filter((v) => v !== val)
          : [...current, val]
      );
      setSearch("");
    },
    [setValue]
  );

  const handleValueRemove = React.useCallback(
    (val: string) => {
      setValue((current) => current.filter((v) => v !== val));
    },
    [setValue]
  );

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
        <Combobox.Options>
          <ScrollArea.Autosize mah={200}>
            {options.length > 0 ? (
              options
            ) : (
              <Combobox.Empty>Nothing found...</Combobox.Empty>
            )}
          </ScrollArea.Autosize>
        </Combobox.Options>
        <Combobox.Footer>
          <Group>
            <Button
              leftSection={items.length === value.length ? <CheckIcon /> : null}
              variant="subtle"
              onClick={() => {
                setValue(items);
              }}
            >
              Select all
            </Button>
            <Button
              leftSection={items.length === value.length ? <CheckIcon /> : null}
              onClick={() => {
                addLandscapes();
                combobox.closeDropdown();
              }}
            >
              Add landscapes
            </Button>
          </Group>
        </Combobox.Footer>
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
    removeIsolatedNodes,
    { toggle: toggleRemoveIsolatedNodes, close: disableRemoveIsolatedNodes },
  ] = useDisclosure(false);
  const [fileList, setFileList] = React.useState<string[]>([]);
  const [selectedFileList, setSelectedFileList] = React.useState<string[]>([]);
  const [loadedLandscapeList, setLoadedLandscapeList] = React.useState<
    string[]
  >([]);
  const form = useForm<{ name: string; data: Record<string, unknown> }>();
  const [opened, { open, close }] = useDisclosure(false);

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
        `http://localhost:8000/api/graph/get_graph?with_idtype_nodes=${!withIdtypeNodes}&remove_isolated_nodes=${removeIsolatedNodes}`,
        { method: "GET" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
      toggleIdtypeNodes();
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, [withIdtypeNodes, removeIsolatedNodes, setGraph, toggleIdtypeNodes]);

  const fetchGraphWithRemoveIsolatedNodes = React.useCallback(async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/graph/get_graph?with_idtype_nodes=${withIdtypeNodes}&remove_isolated_nodes=${!removeIsolatedNodes}`,
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
    removeIsolatedNodes,
    setGraph,
    toggleRemoveIsolatedNodes,
  ]);

  const fetchGraph = React.useCallback(async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/graph/get_graph?with_idtype_nodes=${withIdtypeNodes}&remove_isolated_nodes=${removeIsolatedNodes}`,
        { method: "GET" }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  }, [withIdtypeNodes, removeIsolatedNodes, setGraph]);

  const removeLandscape = React.useCallback(
    async (landscape: string) => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/graph/remove_landscape?landscape_name=${encodeURIComponent(
            landscape
          )}`,
          { method: "DELETE" }
        );
        const data: GraphConfig = await response.json();
        setGraph(data);
        setLoadedLandscapeList((current) =>
          current.filter((l) => l !== landscape)
        );
      } catch (error) {
        console.error("Error fetching graph data:", error);
      }
    },
    [setGraph]
  );

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

  const addCustomLandscape = React.useCallback(async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/graph/add_custom_landscape",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(form.values),
        }
      );
      const data: GraphConfig = await response.json();
      setGraph(data);
    } catch (error) {
      console.error("Error adding custom landscape:", error);
    }
  }, [form.values, setGraph]);

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
      <Modal
        opened={opened}
        onClose={close}
        title="Add Custom Landscape"
        size="auto"
      >
        <form>
          <Stack miw={400}>
            <TextInput label="Landscape Name" {...form.getInputProps("name")} />
            <Textarea
              resize="both"
              minRows={8}
              maxRows={24}
              label="Landscape Data (JSON)"
              styles={{ input: { fontFamily: "monospace", fontSize: 12 } }}
              {...form.getInputProps("data")}
            />
            <Group justify="flex-end">
              <Button
                type="submit"
                onClick={(e) => {
                  e.preventDefault();
                  addCustomLandscape();
                  close();
                }}
                disabled={!form.isValid()}
              >
                Add Landscape
              </Button>
              <Button variant="outline" onClick={close}>
                Cancel
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>
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
              <HoverCard>
                <HoverCard.Target>
                  <Badge color="blue" variant="light">
                    {loadedLandscapeList.length}
                  </Badge>
                </HoverCard.Target>
                <HoverCard.Dropdown>
                  <Stack>
                    <Text>Currently loaded landscapes:</Text>
                    <ScrollArea.Autosize mah={200}>
                      <Stack gap="xs">
                        {loadedLandscapeList.map((landscape) => (
                          <Group
                            key={landscape}
                            justify="space-between"
                            wrap="nowrap"
                          >
                            <Text size="sm">{landscape}</Text>
                            <Group>
                              <ActionIcon
                                color="red"
                                size="sm"
                                variant="light"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  removeLandscape(landscape);
                                }}
                              >
                                <IconTrash />
                              </ActionIcon>
                            </Group>
                          </Group>
                        ))}
                      </Stack>
                    </ScrollArea.Autosize>
                  </Stack>
                </HoverCard.Dropdown>
              </HoverCard>
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
                  addLandscapes={addLandscapes}
                />
                <Button
                  onClick={addLandscapes}
                  disabled={selectedFileList.length === 0}
                >
                  Add selected landscapes
                </Button>

                <Divider label="Custom landscapes" />
                <Button onClick={open}>Add a custom landscape</Button>
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
      <Box
        style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}
      >
        <Button
          onClick={() => {
            setGraphMode("2d");
            fetchResetGraph();
            setSelectedFileList([]);
            enableWithIdtypeNodes();
            disableRemoveIsolatedNodes();
          }}
          disabled={!graph}
          color="red"
        >
          Reset graph
        </Button>
        <Button
          disabled={loadedLandscapeList.length === 0}
          onClick={fetchGraph}
        >
          Refresh
        </Button>
      </Box>
    </Stack>
  );
}
