import networkx as nx


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


def populate_entity_to_idtype_relations(
    G: nx.MultiDiGraph, landscape_name: str
) -> None:
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
                        "origins": {
                            *(
                                list(
                                    G.edges.get(
                                        (
                                            entity,
                                            idtype,
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


def derive_one_to_one_relations_from_idtype(
    G: nx.MultiDiGraph, idtype: dict, landscape_name: str
) -> None:
    idtype_node_id = idtype.get("id")
    connected_entities = [
        neighbor
        for neighbor in G.predecessors(idtype_node_id)
        if G.nodes.get(neighbor, {}).get("data", {}).get("type") == "entity"
    ]
    for i in range(len(connected_entities)):
        for j in range(i + 1, len(connected_entities)):
            G.add_edge(
                connected_entities[i],
                connected_entities[j],
                data={
                    "type": "1-1",
                    "via_idtype": idtype_node_id,
                    "source": {
                        "entityId": connected_entities[i],
                        # TODO: check if these two entities are connected by more than one column
                        # In this case, we need to extend this list to include all such columns,
                        # just like we do for determining origins
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
                },
            )
            G.add_edge(
                connected_entities[j],
                connected_entities[i],
                data={
                    "type": "1-1",
                    "via_idtype": idtype_node_id,
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
                },
            )


def populate_one_to_n_relation(
    G: nx.MultiDiGraph, relation: dict, landscape_name: str
) -> None:
    G.add_edge(
        relation.get("source", {"id": None}).get("id"),
        relation.get("target", {"id": None}).get("id"),
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
        G.add_edge(
            relation.get("target", {"id": None}).get("id"),
            relation.get("source", {"id": None}).get("id"),
            data={
                **relation,
                "type": "n-1",
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
    pass


def populate_ordino_drilldown_relation(
    G: nx.MultiDiGraph, relation: dict, landscape_name: str
) -> None:
    # direct connection from source to target
    G.add_edge(
        relation.get("source", {"id": None}).get("id"),
        relation.get("target", {"id": None}).get("id"),
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
    G.add_edge(
        relation.get("target", {"id": None}).get("id"),
        relation.get("source", {"id": None}).get("id"),
        data={
            **relation,
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
    for mapping_index, mapping in enumerate(relation.get("mapping", [])):
        # connections via the mapping entity as a fragment of the drilldown relation
        G.add_edge(
            relation.get("source", {"id": None}).get("id"),
            mapping.get("entity"),
            data={
                **relation,
                "type": "ordino-drilldown-fragment",
                "mapping": mapping,
                "origins": {
                    *(
                        list(
                            G.edges.get(
                                (
                                    relation.get("source", {"id": None}).get("id"),
                                    mapping.get("entity"),
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

        G.add_edge(
            mapping.get("entity"),
            relation.get("source", {"id": None}).get("id"),
            data={
                **relation,
                "type": "ordino-drilldown-fragment",
                "mapping": mapping,
                "origins": {
                    *(
                        list(
                            G.edges.get(
                                (
                                    mapping.get("entity"),
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

        G.add_edge(
            mapping.get("entity"),
            relation.get("target", {"id": None}).get("id"),
            data={
                **relation,
                "type": "ordino-drilldown-fragment",
                "mapping": mapping,
                "origins": {
                    *(
                        list(
                            G.edges.get(
                                (
                                    mapping.get("entity"),
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

        G.add_edge(
            relation.get("target", {"id": None}).get("id"),
            mapping.get("entity"),
            data={
                **relation,
                "type": "ordino-drilldown-fragment",
                "mapping": mapping,
                "origins": {
                    *(
                        list(
                            G.edges.get(
                                (
                                    relation.get("target", {"id": None}).get("id"),
                                    mapping.get("entity"),
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


def populate_graph(G: nx.MultiDiGraph, payload: dict, landscape_name: str) -> None:
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


def populate_idtype_relations(G: nx.MultiDiGraph, landscape_name: str) -> None:
    populate_entity_to_idtype_relations(G, landscape_name)
    for n, attr in G.nodes.data():
        if attr.get("data", {}).get("type") == "idtype":
            derive_one_to_one_relations_from_idtype(
                G, attr.get("data", {}), landscape_name
            )


def populate_one_to_n_relations(
    G: nx.MultiDiGraph, payload: dict, landscape_name: str
) -> None:
    for relation in payload.get("relations", []):
        if relation.get("type") == "1-n":
            populate_one_to_n_relation(G, relation, landscape_name)


def populate_ordino_drilldown_relations(
    G: nx.MultiDiGraph, payload: dict, landscape_name: str
) -> None:
    for relation in payload.get("relations", []):
        if relation.get("type") == "ordino-drilldown":
            populate_ordino_drilldown_relation(G, relation, landscape_name)


def get_relations_for_node(G: nx.MultiDiGraph, node_id: str) -> list[dict]:
    relations = []
    if node_id not in G:
        return relations

    for neighbor in G.neighbors(node_id):
        for key in G[node_id][neighbor]:
            edge_data = G[node_id][neighbor][key].get("data", {})
            if edge_data.get("type") not in [
                "ordino-drilldown-fragment",
                "idtype-mapping",
            ]:
                relations.append(
                    {
                        "source": node_id,
                        "target": neighbor,
                        "data": edge_data,
                    }
                )

    for predecessor in G.predecessors(node_id):
        for key in G[predecessor][node_id]:
            edge_data = G[predecessor][node_id][key].get("data", {})
            if edge_data.get("type") not in [
                "ordino-drilldown-fragment",
                "idtype-mapping",
            ]:
                relations.append(
                    {
                        "source": predecessor,
                        "target": node_id,
                        "data": edge_data,
                    }
                )

    return relations
