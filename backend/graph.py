import networkx as nx

from landscape_merge import get_relation_string


def populate_idtype_nodes(
    G: nx.MultiDiGraph, idtypes: list[dict], landscape_name: str
) -> None:
    for idtype in idtypes:
        G.add_node(
            idtype.get("id"),
            data={
                "type": "idtype",
                "origins": {
                    *(
                        list(
                            G.nodes.get(idtype.get("id"), {})
                            .get("data", {})
                            .get("origins", [])
                        )
                        + [landscape_name]
                    )
                },
                **idtype,
            },
        )


def populate_entity_nodes(
    G: nx.MultiDiGraph, entities: list[dict], landscape_name: str
) -> None:
    for entity in entities:
        G.add_node(
            entity.get("id"),
            data={
                "type": "entity",
                "origins": {
                    *(
                        list(
                            G.nodes.get(entity.get("id"), {})
                            .get("data", {})
                            .get("origins", [])
                        )
                        + [landscape_name]
                    )
                },
                **entity,
            },
        )


def populate_idtype_mapping_relations(G: nx.MultiDiGraph, landscape_name: str) -> None:
    entities_in_graph_with_idtype_columns = [
        (
            n,
            [
                col
                for col in attr.get("data", {}).get("columns", [])
                if col.get("idtype", None) is not None
            ],
        )
        for n, attr in G.nodes(data=True)
        if attr.get("data", {}).get("type") == "entity"
    ]
    idtypes_in_graph = [
        n
        for n, attr in G.nodes(data=True)
        if attr.get("data", {}).get("type") == "idtype"
    ]
    for entity, columns in entities_in_graph_with_idtype_columns:
        for col in columns:
            idtype = col.get("idtype")
            if idtype in idtypes_in_graph:
                relation = {
                    "type": "idtype-mapping",
                    "column": col.get("columnName"),
                    "entityId": entity,
                    "is_derived": True,
                }
                relation_hash, _ = get_relation_string(relation)
                G.add_edge(
                    entity,
                    idtype,
                    key=relation_hash,
                    data={
                        **relation,
                        "origins": {
                            *(
                                list(
                                    G.edges.get(
                                        (
                                            entity,
                                            idtype,
                                            relation_hash,  # For MultiDiGraph, need to specify the key
                                        ),
                                        {},
                                    )
                                    .get("data", {})
                                    .get("origins", [])
                                )
                                + [landscape_name]
                            )
                        },
                    },
                )


def derive_one_to_one_relations_from_idtype(
    G: nx.MultiDiGraph, idtype: dict, landscape_name: str
) -> None:
    idtype_node_id = idtype.get("id")
    connected_entities = [
        predecessor
        for predecessor in G.predecessors(idtype_node_id)
        if G.nodes.get(predecessor, {}).get("data", {}).get("type") == "entity"
    ]
    for i in range(len(connected_entities)):
        for j in range(i + 1, len(connected_entities)):
            forward_relation = {
                "type": "1-1",
                "via_idtype": idtype_node_id,
                "is_derived": True,
                "source": {
                    "entityId": connected_entities[i],
                    "columns": [
                        col
                        for col in G.nodes.get(connected_entities[i], {})
                        .get("data", {})
                        .get("columns", [])
                        if col.get("idtype") == idtype_node_id
                    ],
                },
                "target": {
                    "entityId": connected_entities[j],
                    "columns": [
                        col
                        for col in G.nodes.get(connected_entities[j], {})
                        .get("data", {})
                        .get("columns", [])
                        if col.get("idtype") == idtype_node_id
                    ],
                },
            }
            forward_relation_hash, _ = get_relation_string(forward_relation)
            reverse_relation = {
                "type": "1-1",
                "via_idtype": idtype_node_id,
                "is_derived": True,
                "source": {
                    "entityId": connected_entities[j],
                    "columns": [
                        col
                        for col in G.nodes.get(connected_entities[j], {})
                        .get("data", {})
                        .get("columns", [])
                        if col.get("idtype") == idtype_node_id
                    ],
                },
                "target": {
                    "entityId": connected_entities[i],
                    "columns": [
                        col
                        for col in G.nodes.get(connected_entities[i], {})
                        .get("data", {})
                        .get("columns", [])
                        if col.get("idtype") == idtype_node_id
                    ],
                },
            }
            reverse_relation_hash, _ = get_relation_string(reverse_relation)
            G.add_edge(
                connected_entities[i],
                connected_entities[j],
                key=forward_relation_hash,
                data={
                    "via_idtype": idtype_node_id,
                    "origins": {
                        *(
                            list(
                                G.edges.get(
                                    (
                                        connected_entities[i],
                                        connected_entities[j],
                                        0,  # For MultiDiGraph, need to specify the key
                                    ),
                                    {},
                                )
                                .get("data", {})
                                .get("origins", [])
                            )
                            + [landscape_name]
                        )
                    },
                    **forward_relation,
                },
            )
            G.add_edge(
                connected_entities[j],
                connected_entities[i],
                key=reverse_relation_hash,
                data={
                    "via_idtype": idtype_node_id,
                    "origins": {
                        *(
                            list(
                                G.edges.get(
                                    (
                                        connected_entities[j],
                                        connected_entities[i],
                                        0,  # For MultiDiGraph, need to specify the key
                                    ),
                                    {},
                                )
                                .get("data", {})
                                .get("origins", [])
                            )
                            + [landscape_name]
                        )
                    },
                    **reverse_relation,
                },
            )


def populate_graph(payload: dict, landscape_name: str) -> nx.MultiDiGraph:
    G = nx.MultiDiGraph()
    populate_idtype_nodes(G, payload.get("idtypes", []), landscape_name=landscape_name)

    entities = [
        {
            "id": f"{db.get('id')}.{schema.get('name')}.{entity.get('tableName')}"
            if schema.get("name") is not None
            else f"{db.get('id')}.{entity.get('tableName')}",
            **entity,
        }
        for db in payload.get("databases", [])
        for schema in db.get("schemas", [])
        for entity in schema.get("entities", [])
    ]

    populate_entity_nodes(G, entities, landscape_name=landscape_name)

    return G


def populate_idtype_relations(
    G: nx.MultiDiGraph, landscape_name: str
) -> nx.MultiDiGraph:
    populate_idtype_mapping_relations(G, landscape_name)
    for n, attr in G.nodes(data=True):
        if attr.get("data", {}).get("type") == "idtype":
            derive_one_to_one_relations_from_idtype(
                G, attr.get("data", {}), landscape_name
            )
    return G


def populate_one_to_n_relations(
    G: nx.MultiDiGraph, payload: dict, landscape_name: str
) -> nx.MultiDiGraph:
    for relation in payload.get("relations", []):
        if relation.get("type") == "1-n":
            relation_hash, _ = get_relation_string(relation)
            G.add_edge(
                relation.get("source", {"id": None}).get("id"),
                relation.get("target", {"id": None}).get("id"),
                key=relation_hash,
                data={
                    **relation,
                    "origins": {
                        *(
                            list(
                                G.edges.get(
                                    (
                                        relation.get("source", {"id": None}).get("id"),
                                        relation.get("target", {"id": None}).get("id"),
                                        0,  # For MultiDiGraph, need to specify the key
                                    ),
                                    {},
                                )
                                .get("data", {})
                                .get("origins", [])
                            )
                            + [landscape_name]
                        )
                    },
                },
            )
            if relation.get("bidirectional", False):
                reverse_relation_hash, _ = get_relation_string(relation)
                G.add_edge(
                    relation.get("target", {"id": None}).get("id"),
                    relation.get("source", {"id": None}).get("id"),
                    key=reverse_relation_hash,
                    data={
                        **relation,
                        "type": "n-1",
                        "is_derived": True,
                        "origins": {
                            *(
                                list(
                                    G.edges.get(
                                        (
                                            relation.get("target", {"id": None}).get(
                                                "id"
                                            ),
                                            relation.get("source", {"id": None}).get(
                                                "id"
                                            ),
                                            0,  # For MultiDiGraph, need to specify the key
                                        ),
                                        {},
                                    )
                                    .get("data", {})
                                    .get("origins", [])
                                )
                                + [landscape_name]
                            )
                        },
                    },
                )
    return G


def populate_ordino_drilldown_relations(
    G: nx.MultiDiGraph, payload: dict, landscape_name: str
) -> nx.MultiDiGraph:
    for relation in payload.get("relations", []):
        if relation.get("type") == "ordino-drilldown":
            relation_hash, _ = get_relation_string(relation)
            # direct connection from source to target
            G.add_edge(
                relation.get("source", {"id": None}).get("id"),
                relation.get("target", {"id": None}).get("id"),
                key=relation_hash,
                data={
                    **relation,
                    "origins": {
                        *(
                            list(
                                G.edges.get(
                                    (
                                        relation.get("source", {"id": None}).get("id"),
                                        relation.get("target", {"id": None}).get("id"),
                                        0,  # For MultiDiGraph, need to specify the key
                                    ),
                                    {},
                                )
                                .get("data", {})
                                .get("origins", [])
                            )
                            + [landscape_name]
                        )
                    },
                },
            )

            # direct connection from target to source
            reverse_relation = {
                **relation,
                "is_derived": True,
                "source": relation.get("target"),
                "target": relation.get("source"),
            }
            reverse_relation_hash, _ = get_relation_string(reverse_relation)
            G.add_edge(
                relation.get("target", {"id": None}).get("id"),
                relation.get("source", {"id": None}).get("id"),
                key=reverse_relation_hash,
                data={
                    **reverse_relation,
                    "origins": {
                        *(
                            list(
                                G.edges.get(
                                    (
                                        relation.get("target", {"id": None}).get("id"),
                                        relation.get("source", {"id": None}).get("id"),
                                        0,  # For MultiDiGraph, need to specify the key
                                    ),
                                    {},
                                )
                                .get("data", {})
                                .get("origins", [])
                            )
                            + [landscape_name]
                        )
                    },
                },
            )
            # for mapping_index, mapping in enumerate(relation.get("mapping", [])):
            #     # connections via the mapping entity as a fragment of the drilldown relation
            #     G.add_edge(
            #         relation.get("source", {"id": None}).get("id"),
            #         mapping.get("entity"),
            #         data={
            #             **relation,
            #             "type": "ordino-drilldown-fragment",
            #             "is_derived": True,
            #             "mapping": mapping,
            #             "origins": {
            #                 *(
            #                     list(
            #                         G.edges.get(
            #                             (
            #                                 relation.get("source", {"id": None}).get(
            #                                     "id"
            #                                 ),
            #                                 mapping.get("entity"),
            #                                 0,  # For MultiDiGraph, need to specify the key
            #                             ),
            #                             {},
            #                         )
            #                         .get("data", {})
            #                         .get("origins", [])
            #                     )
            #                     + [landscape_name]
            #                 )
            #             },
            #         },
            #     )

            #     G.add_edge(
            #         mapping.get("entity"),
            #         relation.get("source", {"id": None}).get("id"),
            #         data={
            #             **relation,
            #             "type": "ordino-drilldown-fragment",
            #             "is_derived": True,
            #             "mapping": mapping,
            #             "origins": {
            #                 *(
            #                     list(
            #                         G.edges.get(
            #                             (
            #                                 mapping.get("entity"),
            #                                 relation.get("source", {"id": None}).get(
            #                                     "id"
            #                                 ),
            #                                 0,  # For MultiDiGraph, need to specify the key
            #                             ),
            #                             {},
            #                         )
            #                         .get("data", {})
            #                         .get("origins", [])
            #                     )
            #                     + [landscape_name]
            #                 )
            #             },
            #         },
            #     )

            #     G.add_edge(
            #         mapping.get("entity"),
            #         relation.get("target", {"id": None}).get("id"),
            #         data={
            #             **relation,
            #             "type": "ordino-drilldown-fragment",
            #             "is_derived": True,
            #             "mapping": mapping,
            #             "origins": {
            #                 *(
            #                     list(
            #                         G.edges.get(
            #                             (
            #                                 mapping.get("entity"),
            #                                 relation.get("target", {"id": None}).get(
            #                                     "id"
            #                                 ),
            #                                 0,  # For MultiDiGraph, need to specify the key
            #                             ),
            #                             {},
            #                         )
            #                         .get("data", {})
            #                         .get("origins", [])
            #                     )
            #                     + [landscape_name]
            #                 )
            #             },
            #         },
            #     )

            #     G.add_edge(
            #         relation.get("target", {"id": None}).get("id"),
            #         mapping.get("entity"),
            #         data={
            #             **relation,
            #             "type": "ordino-drilldown-fragment",
            #             "is_derived": True,
            #             "mapping": mapping,
            #             "origins": {
            #                 *(
            #                     list(
            #                         G.edges.get(
            #                             (
            #                                 relation.get("target", {"id": None}).get(
            #                                     "id"
            #                                 ),
            #                                 mapping.get("entity"),
            #                                 0,  # For MultiDiGraph, need to specify the key
            #                             ),
            #                             {},
            #                         )
            #                         .get("data", {})
            #                         .get("origins", [])
            #                     )
            #                     + [landscape_name]
            #                 )
            #             },
            #         },
            #     )
    return G


def get_relations_for_node(G: nx.MultiDiGraph, node_id: str) -> list[dict]:
    relations = []
    if node_id not in G:
        return relations

    for adjacent in list(G.neighbors(node_id)) + list(G.predecessors(node_id)):
        for key in G[node_id][adjacent]:
            edge_data = G[node_id][adjacent][key].get("data", {})
            if not edge_data.get("is_derived", False):
                relations.append(
                    {
                        "source": node_id,
                        "target": adjacent,
                        "data": edge_data,
                    }
                )

    return relations


def merge_graphs(
    Gs: list[nx.MultiDiGraph],
) -> nx.MultiDiGraph:
    G_merged = nx.compose_all(Gs)
    return G_merged


def deduplicate_relations(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
    idtype_relations = [
        (u, v, k, attr)
        for u, v, k, attr in G.edges(data=True, keys=True)
        if attr.get("data", {}).get("type") == "1-1"
        and attr.get("data", {}).get("via_idtype") is not None
    ]

    one_to_n_relations = [
        (u, v, k, attr)
        for u, v, k, attr in G.edges(data=True, keys=True)
        if attr.get("data", {}).get("type") == "1-n"
    ]

    # ordino_drilldown_relations = [
    #     (u, v, k, attr)
    #     for u, v, k, attr in G.edges(data=True, keys=True)
    #     if attr.get("data", {}).get("type") == "ordino-drilldown"
    # ]

    # find all the edges which have the same u and v
    uniques = []
    duplicates = []
    for relations in [one_to_n_relations, idtype_relations]:
        for u, v, k, _ in relations:
            edge_signature = f"{u}-{v}"
            if edge_signature not in uniques:
                uniques.append(edge_signature)
            else:
                duplicates.append((u, v, k))

    for u, v, k in duplicates:
        G.remove_edge(u, v, k)

    # # find all the edges which have the same u and v
    # uniques = []
    # duplicates = []
    # for relations in [ordino_drilldown_relations, idtype_relations]:
    #     for u, v, k, attr in relations:
    #         edge_signature = f"{u}-{v}"
    #         if attr.get("data", {}).get("type", "") == "ordino_drilldown":
    #             reverse_edge_signature = f"{v}-{u}"
    #             uniques.append(edge_signature)
    #             uniques.append(reverse_edge_signature)
    #         elif edge_signature not in uniques:
    #             uniques.append(edge_signature)
    #         else:
    #             duplicates.append((u, v, k))

    # for u, v, k in duplicates:
    #     G.remove_edge(u, v, k)

    return G


def get_subgraph_with_idtype_nodes(
    G: nx.MultiDiGraph, with_idtype_nodes: bool
) -> nx.MultiDiGraph:
    if with_idtype_nodes:
        return G
    else:
        SG = G.copy()
        nodes_to_hide = [
            n
            for n, attr in G.nodes(data=True)
            if attr.get("data", {}).get("type") == "idtype"
        ]
        filter = nx.filters.hide_nodes(nodes_to_hide)
        SG = nx.subgraph_view(SG, filter_node=filter)
        return SG


def get_subgraph_with_isolated_nodes_removed(
    G: nx.MultiDiGraph, remove_isolated_nodes: bool
) -> nx.MultiDiGraph:
    SG = G.copy()

    if remove_isolated_nodes:
        SG.remove_nodes_from(list(nx.isolates(G)))

    return SG
