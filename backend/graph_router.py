from fastapi import APIRouter, HTTPException
import json
from networkx.readwrite import json_graph
import networkx as nx
from graph import (
    populate_graph,
    populate_idtype_relations,
    populate_one_to_n_relations,
    populate_ordino_drilldown_relations,
)

graph_router = APIRouter(prefix="/api/graph")

# In-memory storage for the graph and landscape data
G = nx.MultiDiGraph()
landscape = {}


@graph_router.post("/populate_graph")
def populate_graph_route():
    global G, landscape
    # Load landscape data from file
    landscape = json.load(open("data/visyn_kb.json"))
    # Create the initial graph
    G = populate_graph(G, landscape, landscape_name="visyn_kb")
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
    data = json_graph.node_link_data(G)
    return data
