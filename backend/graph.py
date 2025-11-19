import networkx as nx


def populate_idtype_nodes(
    G: nx.MultiDiGraph, idtypes: list[dict], landscape_name: str
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
    G: nx.MultiDiGraph, entities: list[dict], landscape_name: str
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


def populate_idtype_relations(G: nx.MultiDiGraph, landscape_name: str) -> None:
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


def populate_one_to_n_relation(
    G: nx.MultiDiGraph, relation: dict, landscape_name: str
) -> None:
    G.add_edge(
        relation.get("source", {"id": None}).get("id"),
        relation.get("target", {"id": None}).get("id"),
        data={
            **relation,
            "origins": G.edges.get(
                (
                    relation.get("source", {"id": None}).get("id"),
                    relation.get("target", {"id": None}).get("id"),
                    0,  # For MultiDiGraph, need to specify the key
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
    pass


def populate_ordino_drilldown_relation(
    G: nx.MultiDiGraph, relation: dict, landscape_name: str
) -> None:
    for mapping_index, mapping in enumerate(relation.get("mapping", [])):
        # direct connection from source to target
        G.add_edge(
            relation.get("source", {"id": None}).get("id"),
            relation.get("target", {"id": None}).get("id"),
            data={
                **relation,
                "mapping": mapping,
                "origins": G.edges.get(
                    (
                        relation.get("source", {"id": None}).get("id"),
                        relation.get("target", {"id": None}).get("id"),
                        mapping_index,  # For MultiDiGraph, need to specify the key
                    ),
                    {},
                )
                .get("data", {})
                .get("origins", [])
                + [landscape_name],
            },
        )

        # direct connection from target to source
        G.add_edge(
            relation.get("target", {"id": None}).get("id"),
            relation.get("source", {"id": None}).get("id"),
            data={
                **relation,
                "type": "ordino-drilldown",
                "mapping": mapping,
                "origins": G.edges.get(
                    (
                        relation.get("target", {"id": None}).get("id"),
                        relation.get("source", {"id": None}).get("id"),
                        mapping_index,  # For MultiDiGraph, need to specify the key
                    ),
                    {},
                )
                .get("data", {})
                .get("origins", [])
                + [landscape_name],
            },
        )

        # connections via the mapping entity as a fragment of the drilldown relation
        G.add_edge(
            relation.get("source", {"id": None}).get("id"),
            mapping.get("entity"),
            data={
                **relation,
                "type": "ordino-drilldown-fragment",
                "mapping": mapping,
                "origins": G.edges.get(
                    (
                        relation.get("source", {"id": None}).get("id"),
                        mapping.get("entity"),
                        0,  # For MultiDiGraph, need to specify the key
                    ),
                    {},
                )
                .get("data", {})
                .get("origins", [])
                + [landscape_name],
            },
        )

        G.add_edge(
            mapping.get("entity"),
            relation.get("source", {"id": None}).get("id"),
            data={
                **relation,
                "type": "ordino-drilldown-fragment",
                "mapping": mapping,
                "origins": G.edges.get(
                    (
                        mapping.get("entity"),
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

        G.add_edge(
            mapping.get("entity"),
            relation.get("target", {"id": None}).get("id"),
            data={
                **relation,
                "type": "ordino-drilldown-fragment",
                "mapping": mapping,
                "origins": G.edges.get(
                    (
                        mapping.get("entity"),
                        relation.get("target", {"id": None}).get("id"),
                        0,  # For MultiDiGraph, need to specify the key
                    ),
                    {},
                )
                .get("data", {})
                .get("origins", [])
                + [landscape_name],
            },
        )

        G.add_edge(
            relation.get("target", {"id": None}).get("id"),
            mapping.get("entity"),
            data={
                **relation,
                "type": "ordino-drilldown-fragment",
                "mapping": mapping,
                "origins": G.edges.get(
                    (
                        relation.get("target", {"id": None}).get("id"),
                        mapping.get("entity"),
                        0,  # For MultiDiGraph, need to specify the key
                    ),
                    {},
                )
                .get("data", {})
                .get("origins", [])
                + [landscape_name],
            },
        )


def populate_configured_relations(
    G: nx.MultiDiGraph, relations: list[dict], landscape_name: str
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
                populate_one_to_n_relation(G, relation, landscape_name)
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
                populate_ordino_drilldown_relation(G, relation, landscape_name)


def populate_graph(
    G: nx.MultiDiGraph, payload: dict, landscape_name: str
) -> nx.MultiDiGraph:
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
    return G


def populate_one_to_n_relations(
    G: nx.MultiDiGraph, payload: dict, landscape_name: str
) -> nx.MultiDiGraph:
    for relation in payload.get("relations", []):
        if relation.get("type") == "1-n":
            populate_one_to_n_relation(G, relation, landscape_name)
    return G


def populate_ordino_drilldown_relations(
    G: nx.MultiDiGraph, payload: dict, landscape_name: str
) -> nx.MultiDiGraph:
    for relation in payload.get("relations", []):
        if relation.get("type") == "ordino-drilldown":
            populate_ordino_drilldown_relation(G, relation, landscape_name)
    return G
