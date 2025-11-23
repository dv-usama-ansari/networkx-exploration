from fastapi import APIRouter, HTTPException
import json
import logging
from networkx.readwrite import json_graph
import networkx as nx
from graph import (
    deduplicate_relations,
    get_relations_for_node,
    get_subgraph_with_idtype_nodes,
    get_subgraph_with_isolated_nodes_removed,
    merge_graphs,
    populate_graph,
    populate_idtype_relations,
    populate_one_to_n_relations,
    populate_ordino_drilldown_relations,
)

graph_router = APIRouter(prefix="/api/graph")

# In-memory storage for the graph and landscape data
G = nx.MultiDiGraph()

loaded_landscapes_map: dict[str, dict] = {}
loaded_landscapes_graph_map: dict[str, nx.MultiDiGraph] = {}

_log = logging.getLogger(__name__)


@graph_router.post("/populate_graph")
def populate_graph_route():
    global G
    # Load landscape data from file
    visyn_kb_json = json.load(open("data/visyn_kb.json"))
    loaded_landscapes_map["visyn_kb"] = visyn_kb_json
    # Create the initial graph
    visyn_kb_graph = populate_graph(visyn_kb_json, landscape_name="visyn_kb")
    visyn_kb_graph = deduplicate_relations(visyn_kb_graph)
    G = merge_graphs([G, visyn_kb_graph])
    loaded_landscapes_graph_map["visyn_kb"] = visyn_kb_graph
    data = json_graph.node_link_data(visyn_kb_graph)
    return data


@graph_router.post("/populate_idtype_relations")
def populate_idtype_relations_route():
    global G
    if G is None:
        raise HTTPException(
            status_code=400,
            detail="Graph not initialized. Please populate the graph first.",
        )

    visyn_kb_graph = loaded_landscapes_graph_map.get("visyn_kb", nx.MultiDiGraph())
    visyn_kb_graph = populate_idtype_relations(
        visyn_kb_graph, landscape_name="visyn_kb"
    )
    visyn_kb_graph = deduplicate_relations(visyn_kb_graph)
    loaded_landscapes_graph_map["visyn_kb"] = visyn_kb_graph
    G = merge_graphs([G, visyn_kb_graph])
    data = json_graph.node_link_data(visyn_kb_graph)
    return data


@graph_router.post("/populate_one_to_n_relations")
def populate_one_to_n_relations_route():
    global G
    if G is None:
        raise HTTPException(
            status_code=400,
            detail="Graph not initialized. Please populate the graph first.",
        )

    visyn_kb_json = loaded_landscapes_map.get("visyn_kb", {})
    visyn_kb_graph = loaded_landscapes_graph_map.get("visyn_kb", nx.MultiDiGraph())

    visyn_kb_graph = populate_one_to_n_relations(
        visyn_kb_graph, visyn_kb_json, landscape_name="visyn_kb"
    )
    visyn_kb_graph = deduplicate_relations(visyn_kb_graph)
    loaded_landscapes_graph_map["visyn_kb"] = visyn_kb_graph
    G = merge_graphs([G, visyn_kb_graph])
    data = json_graph.node_link_data(visyn_kb_graph)
    return data


@graph_router.post("/populate_ordino_drilldown_relations")
def populate_ordino_drilldown_relations_route():
    global G
    if G is None:
        raise HTTPException(
            status_code=400,
            detail="Graph not initialized. Please populate the graph first.",
        )

    visyn_kb_json = loaded_landscapes_map.get("visyn_kb", {})
    visyn_kb_graph = loaded_landscapes_graph_map.get("visyn_kb", nx.MultiDiGraph())
    visyn_kb_graph = populate_ordino_drilldown_relations(
        visyn_kb_graph, visyn_kb_json, landscape_name="visyn_kb"
    )
    visyn_kb_graph = deduplicate_relations(visyn_kb_graph)
    loaded_landscapes_graph_map["visyn_kb"] = visyn_kb_graph
    G = merge_graphs([G, visyn_kb_graph])
    data = json_graph.node_link_data(G)
    return data


@graph_router.get("/get_graph")
def get_graph_route(with_idtype_nodes: bool, remove_isolated_nodes: bool):
    global G
    if G is None:
        raise HTTPException(
            status_code=400,
            detail="Graph not initialized. Please populate the graph first.",
        )

    SG = G.copy()
    SG = deduplicate_relations(SG)
    SG = get_subgraph_with_idtype_nodes(SG, with_idtype_nodes)
    SG = get_subgraph_with_isolated_nodes_removed(SG, remove_isolated_nodes)
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
    global loaded_landscapes_map
    return list(loaded_landscapes_map.keys())


@graph_router.post("/add_landscapes")
def add_landscapes_route(landscape_names: list[str]):
    # global G
    # for landscape_name in landscape_names:
    #     # Load landscape data from file
    #     landscape_json = json.load(open(f"data/{landscape_name}.json"))
    #     # Create the initial graph
    #     populate_graph(G, landscape_json, landscape_name=landscape_name)
    #     loaded_landscapes_map[landscape_name] = landscape_json
    #     populate_idtype_relations(G, landscape_name)
    #     populate_one_to_n_relations(G, landscape_json, landscape_name)
    #     populate_ordino_drilldown_relations(
    #         G, landscape_json, landscape_name=landscape_name
    #     )
    # deduplicate_relations(G)
    # data = json_graph.node_link_data(G)
    # return data
    pass


@graph_router.post("/add_custom_landscape")
def add_custom_landscape_route(payload: dict):
    # global G

    # name: str = payload.get("name", "")
    # data: str = payload.get("data", "{}")

    # # Load landscape data from file
    # landscape_json = json.loads(data)
    # # Create the initial graph
    # populate_graph(G, landscape_json, landscape_name=name)
    # loaded_landscapes_map[name] = landscape_json
    # populate_idtype_relations(G, landscape_name=name)
    # populate_one_to_n_relations(G, landscape_json, landscape_name=name)
    # populate_ordino_drilldown_relations(G, landscape_json, landscape_name=name)
    # deduplicate_relations(G)
    # data = json_graph.node_link_data(G)
    # return data
    pass


@graph_router.post("/remove_landscape")
def remove_landscape_route(landscape_name: str):
#     global G

#     # Load landscape data from file
#     landscape_json = json.loads(data)
#     # Create the initial graph
#     populate_graph(G, landscape_json, landscape_name=name)
#     loaded_landscapes_set.add(name)
#     populate_idtype_relations(G, landscape_json, landscape_name=name)
#     populate_one_to_n_relations(G, landscape_json, landscape_name=name)
#     populate_ordino_drilldown_relations(
#         G, landscape_json, landscape_name=name
#     )
#     deduplicate_relations(G)
#     data = json_graph.node_link_data(G)
#     return data
    pass


@graph_router.post("/reset_graph")
def reset_graph():
    global G
    if G is None:
        raise HTTPException(
            status_code=400,
            detail="Graph not initialized. Please populate the graph first.",
        )

    G.clear()
    loaded_landscapes_map.clear()
    loaded_landscapes_graph_map.clear()
    return None


@graph_router.get("/get_relations/{node_id}")
def get_relations_route(node_id: str):
    global G
    if G is None:
        raise HTTPException(
            status_code=400,
            detail="Graph not initialized. Please populate the graph first.",
        )

    relations = get_relations_for_node(G, node_id)
    return relations
