import networkx as nx

# G = nx.DiGraph()

# # Add visyn_kb.ordino.genes node
# G.add_node(
#     "visyn_kb.ordino.genes",
#     data={
#         "id": "visyn_kb.ordino.genes",
#         "label": "Gene",
#         "type": "entity",
#         "columns": [
#             {"name": "hgnc_symbol", "idtype": "GeneSymbol"},
#             {"name": "ensembl_gene_id", "idtype": "EnsemblGeneID"},
#             {"name": "entrez_gene_id", "idtype": "EntrezGeneID"},
#         ],
#         "origins": ["visyn_kb.json"],
#     },
# )

# # Add visyn_kb.ordino.celllines and visyn_kb.ordino.mutations nodes
# G.add_nodes_from(
#     [
#         (
#             "visyn_kb.ordino.celllines",
#             {
#                 "data": {
#                     "id": "visyn_kb.ordino.celllines",
#                     "label": "Cell lines",
#                     "type": "entity",
#                     "columns": [
#                         {"name": "depmap_id", "idtype": "DepMapID"},
#                         {"name": "cell_line_name", "idtype": "CelllineName"},
#                     ],
#                     "origins": ["visyn_kb.json"],
#                 }
#             },
#         ),
#         (
#             "visyn_kb.ordino.mutations",
#             {
#                 "data": {
#                     "id": "visyn_kb.ordino.mutations",
#                     "label": "Mutations",
#                     "type": "entity",
#                     "columns": [
#                         {"name": "ensembl_gene_id", "idtype": "EnsemblGeneID"},
#                         {"name": "depmap_id", "idtype": "DepMapID"},
#                         {"name": "mutation_type"},
#                     ],
#                     "origins": ["visyn_kb.json"],
#                 }
#             },
#         ),
#     ]
# )

# # Add GeneSymbol idtype node
# G.add_nodes_from(
#     [
#         (
#             "GeneSymbol",
#             {
#                 "data": {
#                     "id": "GeneSymbol",
#                     "label": "Gene Symbol",
#                     "type": "idtype",
#                     "origins": ["visyn_kb.json"],
#                 }
#             },
#         ),
#         (
#             "EntrezGeneID",
#             {
#                 "data": {
#                     "id": "EntrezGeneID",
#                     "label": "Entrez ID",
#                     "type": "idtype",
#                     "origins": ["visyn_kb.json"],
#                 }
#             },
#         ),
#         (
#             "EnsemblGeneID",
#             {
#                 "data": {
#                     "id": "EnselmblGeneID",
#                     "label": "Ensembl Gene ID",
#                     "type": "idtype",
#                     "origins": ["visyn_kb.json"],
#                 }
#             },
#         ),
#         (
#             "DepMapID",
#             {
#                 "data": {
#                     "id": "DepMapID",
#                     "label": "DepMap ID",
#                     "type": "idtype",
#                     "origins": ["visyn_kb.json"],
#                 }
#             },
#         ),
#         (
#             "CelllineName",
#             {
#                 "data": {
#                     "id": "CelllineName",
#                     "label": "Cellline Name",
#                     "type": "idtype",
#                     "origins": ["visyn_kb.json"],
#                 }
#             },
#         ),
#     ]
# )


# # Add edge between genes and GeneSymbol idtype
# G.add_edges_from(
#     [
#         (
#             "visyn_kb.ordino.genes",
#             "GeneSymbol",
#             {
#                 "data": {
#                     "type": "idtype-mapping",
#                     "columns": ["hgnc_symbol"],
#                     "origins": ["visyn_kb.json"],
#                 }
#             },
#         ),
#         (
#             "visyn_kb.ordino.mutations",
#             "GeneSymbol",
#             {
#                 "data": {
#                     "type": "idtype-mapping",
#                     "columns": ["gene_symbol"],
#                     "origins": ["visyn_kb.json"],
#                 }
#             },
#         ),
#     ]
# )


# # Add edge between genes and celllines via mutations
# G.add_edge(
#     "visyn_kb.ordino.genes",
#     "visyn_kb.ordino.celllines",
#     data={
#         "type": "ordino-drilldown",
#         "mapping": [
#             {
#                 "entity": "visyn_kb.ordino.mutations",
#                 "sourceKey": "hgnc_symbol",
#                 "targetKey": "depmap_id",
#             }
#         ],
#         "source": {"key": "hgnc_symbol"},
#         "target": {"key": "depmap_id"},
#         "origins": ["visyn_kb.json"],
#     },
# )


def populate_idtype_nodes(
    G: nx.DiGraph, idtypes: list[dict], landscape_name: str
) -> None:
    for idtype in idtypes:
        G.add_node(
            idtype.get("id"),
            data={
                "type": "idtype",
                "origins": G.nodes.get(idtype.get("id"), {})
                .get("data", {})
                .get("origins", [])
                + [landscape_name],
                **idtype,
            },
        )


def populate_entity_nodes(
    G: nx.DiGraph, entities: list[dict], landscape_name: str
) -> None:
    for entity in entities:
        G.add_node(
            entity.get("id"),
            data={
                "type": "entity",
                "origins": G.nodes.get(entity.get("id"), {})
                .get("data", {})
                .get("origins", [])
                + [landscape_name],
                **entity,
            },
        )


def populate_idtype_relations(G: nx.DiGraph, landscape_name: str) -> None:
    entities_in_graph_with_idtype_columns = [
        (
            n,
            [
                col
                for col in attr.get("data", {}).get("columns", [])
                if col.get("idtype", None) is not None
            ],
        )
        for n, attr in G.nodes.data()
        if attr.get("data", {}).get("type") == "entity"
    ]
    idtypes_in_graph = [
        n for n, attr in G.nodes.data() if attr.get("data", {}).get("type") == "idtype"
    ]
    for entity, columns in entities_in_graph_with_idtype_columns:
        for col in columns:
            idtype = col.get("idtype")
            if idtype in idtypes_in_graph:
                G.add_edge(
                    entity,
                    idtype,
                    data={
                        "type": "idtype-mapping",
                        "column": col.get("columnName"),
                        "entityId": entity,
                        "origins": [
                            landscape_name,
                        ],
                    },
                )


def populate_configured_relations(
    G: nx.DiGraph, relations: list[dict], landscape_name: str
) -> None:
    for relation in relations:
        match relation.get("type"):
            case "entity-mapping-same-table":
                # This case is covered already by idtype relations
                pass
            case "entity-mapping-reference-tables":
                # Need to discuss this with the team for more clarity
                pass
            case "1-1":
                # Most likely not configured, as it is covered by idtype relations
                pass
            case "1-n":
                G.add_edge(
                    relation.get("source", {"id": None}).get("id"),
                    relation.get("target", {"id": None}).get("id"),
                    data={
                        **relation,
                        "origins": G.edges.get(
                            (
                                relation.get("source", {"id": None}).get("id"),
                                relation.get("target", {"id": None}).get("id"),
                                0, # For MultiDiGraph, need to specify the key
                            ),
                            {},
                        )
                        .get("data", {})
                        .get("origins", [])
                        + [landscape_name],
                    },
                )
                if relation.get("bidirectional", False):
                    G.add_edge(
                        relation.get("target", {"id": None}).get("id"),
                        relation.get("source", {"id": None}).get("id"),
                        data={
                            **relation,
                            "type": "n-1",
                            "origins": G.edges.get(
                                (
                                    relation.get("target", {"id": None}).get("id"),
                                    relation.get("source", {"id": None}).get("id"),
                                    0,  # For MultiDiGraph, need to specify the key
                                ),
                                {},
                            )
                            .get("data", {})
                            .get("origins", [])
                            + [landscape_name],
                        },
                    )
                # pass
            case "n-1":
                # Most likely not configured directly, as it is covered by 1-n relations with bidirectional=True
                pass
            case "1-n-selection":
                pass
            case "m-n":
                pass
            case "m-n-selection":
                pass
            case "ordino-drilldown":
                pass


def get_graph(payload: dict, landscape_name: str) -> nx.Graph:
    G = nx.MultiDiGraph()

    populate_idtype_nodes(G, payload.get("idtypes", []), landscape_name=landscape_name)

    entities = [
        {
            "id": f"{db.get('id')}.{schema.get('name') or 'public'}.{entity.get('tableName')}",
            **entity,
        }
        for db in payload.get("databases", [])
        for schema in db.get("schemas", [])
        for entity in schema.get("entities", [])
    ]

    populate_entity_nodes(G, entities, landscape_name=landscape_name)

    populate_idtype_relations(G, landscape_name=landscape_name)
    populate_configured_relations(
        G, payload.get("relations", []), landscape_name=landscape_name
    )
    return G
