from fastapi import APIRouter, HTTPException
import json
import logging
from networkx.readwrite import json_graph
import networkx as nx
from graph import (
    deduplicate_relations,
    get_relations_for_node,
    get_subgraph_with_idtype_nodes,
    get_subgraph_with_intermediate_edges,
    get_subgraph_with_isolated_nodes_removed,
    populate_graph,
    populate_idtype_relations,
    populate_one_to_n_relations,
    populate_ordino_drilldown_relations,
)

graph_router = APIRouter(prefix="/api/graph")

# In-memory storage for the graph and landscape data
G = nx.MultiDiGraph()
landscape = {}
loaded_landscapes_set = set()

_log = logging.getLogger(__name__)


@graph_router.post("/populate_graph")
def populate_graph_route():
    global G, landscape
    # Load landscape data from file
    landscape = json.load(open("data/visyn_kb.json"))
    loaded_landscapes_set.add("visyn_kb")
    # Create the initial graph
    populate_graph(G, landscape, landscape_name="visyn_kb")
    deduplicate_relations(G)
    data = json_graph.node_link_data(G)
    return data


@graph_router.post("/populate_idtype_relations")
def populate_idtype_relations_route():
    global G
    if G is None:
        raise HTTPException(
            status_code=400,
            detail="Graph not initialized. Please populate the graph first.",
        )

    populate_idtype_relations(G, landscape_name="visyn_kb")
    deduplicate_relations(G)
    data = json_graph.node_link_data(G)
    return data


@graph_router.post("/populate_one_to_n_relations")
def populate_one_to_n_relations_route():
    global G, landscape
    if G is None or landscape is None:
        raise HTTPException(
            status_code=400,
            detail="Graph not initialized. Please populate the graph first.",
        )

    populate_one_to_n_relations(G, landscape, landscape_name="visyn_kb")
    deduplicate_relations(G)
    data = json_graph.node_link_data(G)
    return data


@graph_router.post("/populate_ordino_drilldown_relations")
def populate_ordino_drilldown_relations_route():
    global G, landscape
    if G is None or landscape is None:
        raise HTTPException(
            status_code=400,
            detail="Graph not initialized. Please populate the graph first.",
        )

    populate_ordino_drilldown_relations(G, landscape, landscape_name="visyn_kb")
    deduplicate_relations(G)
    data = json_graph.node_link_data(G)
    return data


@graph_router.get("/get_graph")
def get_graph_route(
    with_idtype_nodes: bool, with_intermediate_edges: bool, remove_isolated_nodes: bool
):
    global G, landscape
    if G is None or landscape is None:
        raise HTTPException(
            status_code=400,
            detail="Graph not initialized. Please populate the graph first.",
        )

    SG = G.copy()
    SG = get_subgraph_with_idtype_nodes(SG, with_idtype_nodes)
    SG = get_subgraph_with_intermediate_edges(SG, with_intermediate_edges)
    SG = get_subgraph_with_isolated_nodes_removed(SG, remove_isolated_nodes)
    deduplicate_relations(SG)
    data = json_graph.node_link_data(SG)

    return data


@graph_router.get("/get_available_landscapes")
def get_available_landscapes_route():
    # For simplicity, we assume the available landscapes are the JSON files in the data directory
    import os

    data_dir = "data"
    landscape_files = [
        f[:-5] for f in os.listdir(data_dir) if f.endswith(".json")
    ]  # Remove .json extension
    return landscape_files


@graph_router.get("/get_loaded_landscapes")
def get_loaded_landscapes_route():
    # For simplicity, we assume the available landscapes are the JSON files in the data directory
    global G, loaded_landscapes_set
    return list(loaded_landscapes_set)


@graph_router.post("/add_landscapes")
def add_landscapes_route(landscape_names: list[str]):
    global G, landscape
    for landscape_name in landscape_names:
        # Load landscape data from file
        landscape = json.load(open(f"data/{landscape_name}.json"))
        # Create the initial graph
        populate_graph(G, landscape, landscape_name=landscape_name)
        loaded_landscapes_set.add(landscape_name)
        populate_idtype_relations(G, landscape_name=landscape_name)
        populate_one_to_n_relations(G, landscape, landscape_name=landscape_name)
        populate_ordino_drilldown_relations(G, landscape, landscape_name=landscape_name)
    deduplicate_relations(G)
    data = json_graph.node_link_data(G)
    return data


@graph_router.post("/reset_graph")
def reset_graph():
    global G, landscape
    if G is None or landscape is None:
        raise HTTPException(
            status_code=400,
            detail="Graph not initialized. Please populate the graph first.",
        )

    G.clear()
    landscape = {}
    loaded_landscapes_set.clear()
    return None


@graph_router.get("/get_relations/{node_id}")
def get_relations_route(node_id: str):
    global G, landscape
    if G is None or landscape is None:
        raise HTTPException(
            status_code=400,
            detail="Graph not initialized. Please populate the graph first.",
        )

    relations = get_relations_for_node(G, node_id)
    return relations
