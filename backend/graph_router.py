from fastapi import APIRouter
import json
from networkx.readwrite import json_graph
from graph import get_graph

graph_router = APIRouter(prefix="/api/graph")


@graph_router.get("/json")
def get_json_graph():
    landscape: dict = json.load(open("data/visyn_kb.json"))
    G = get_graph(landscape, landscape_name="visyn_kb")
    data = json_graph.node_link_data(G)
    return data
