import networkx as nx
from uuid import uuid4 as uuid
import random


def generate_landscape_with_random_uploaded_dataset(
    G: nx.MultiDiGraph, payload: dict
) -> tuple[str, dict]:
    entities = [
        attr.get("data")
        for n, attr in G.nodes(data=True)
        if attr.get("data", {"type": None}).get("type") == "entity"
    ]

    idtypes = [
        n
        for n, attr in G.nodes(data=True)
        if attr.get("data", {"type": None}).get("type") == "idtype"
    ]

    random_entity_name = [
        "Gene",
        "Cellline",
        "Protein",
        "Compound",
        "Disease",
        "Tissue",
    ][random.randint(0, 5)]

    random_entity_configuration = random.choice(entities) if entities else {}
    all_columns = [
        c
        for entity in entities
        for c in entity.get("columns", [])
        if entity is not None
    ]
    random_entity_columns = (
        random.choices(
            [
                c
                for entity in entities
                for c in entity.get("columns", [])
                if entity is not None
            ],
            k=random.randint(3, len(all_columns)) if all_columns else 0,
        )
        if entities
        else []
    )
    random_columns_with_idtypes = [
        {**c, "idtype": random.choice(idtypes) if idtypes else None}
        if random.random() < 0.7
        else c
        for c in random_entity_columns
    ]

    unique_id = f"db.upload.{uuid().hex}"
    random_entity = {
        **random_entity_configuration,
        "id": unique_id,
        "name": f"Uploaded {random_entity_name}",
        "type": "entity",
        "isUploaded": True,
        "columns": random_columns_with_idtypes,
    }

    output_landscape = {
        **payload,
        "databases": [
            {
                **payload.get("databases", [{}])[0],
                "schemas": [
                    {
                        **payload.get("databases", [{}])[0].get("schemas", [{}])[0],
                        "entities": payload.get("databases", [{}])[0]
                        .get("schemas", [{}])[0]
                        .get("entities", [])
                        + [random_entity],
                    }
                ],
            }
        ],
    }

    return (unique_id, output_landscape)
