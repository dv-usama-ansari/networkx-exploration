import hashlib
import json
import logging
from typing import Literal

_log = logging.getLogger(__name__)

LOG_LEVEL_DICT = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def _construct_minified_relation_dict(relation: dict, with_mapping: bool = False, with_workbench: bool = False) -> dict:
    minified_relation = {
        "type": relation.get("type"),
        "source": {"id": relation.get("source", {}).get("id"), "key": relation.get("source", {}).get("key")},
        "target": {"id": relation.get("target", {}).get("id"), "key": relation.get("target", {}).get("key")},
    }
    if with_mapping and relation.get("mapping"):
        minified_relation["mapping"] = [
            {
                "entity": m.get("entity"),
                "sourceKey": m.get("sourceKey"),
                "targetKey": m.get("targetKey"),
                "columns": [c.get("columnName") for c in m.get("columns", [])] if m.get("columns") else [],
            }
            for m in relation.get("mapping", [])
        ]
    if with_workbench and relation.get("workbench"):
        minified_relation["workbench"] = {
            "views": [{"type": v.get("type", "")} for v in relation.get("workbench", {}).get("views", []) or []],
        }
    return minified_relation


def _get_minified_relation(relation: dict) -> dict:
    match relation.get("type"):
        case "1-1":
            minified_relation = _construct_minified_relation_dict(relation)
            return minified_relation
        case "1-n":
            return {
                "type": relation.get("type"),
                "source": {"id": relation.get("source", {}).get("id"), "key": relation.get("source", {}).get("key")},
                "target": {"id": relation.get("target", {}).get("id"), "key": relation.get("target", {}).get("key")},
            }
        case "1-n-selection":
            minified_relation = _construct_minified_relation_dict(relation)
            return minified_relation
        case "n-1":
            minified_relation = _construct_minified_relation_dict(relation)
            return minified_relation
        case "m-n":
            minified_relation = _construct_minified_relation_dict(relation, with_mapping=True)
            return minified_relation
        case "m-n-selection":
            minified_relation = _construct_minified_relation_dict(relation, with_mapping=True)
            return minified_relation
        case "entity-mapping-same-table":
            return {
                "type": relation.get("type"),
                "entity": relation.get("entity"),
            }
        case "entity-mapping-reference-table":
            minified_relation = _construct_minified_relation_dict(relation, with_mapping=True)
            return minified_relation
        case "ordino-drilldown":
            minified_relation = _construct_minified_relation_dict(relation, with_mapping=True, with_workbench=True)
            return minified_relation
        case _:
            return relation


def get_relation_string(relation: dict) -> tuple[str, str]:
    minified_relation = _get_minified_relation(dict(sorted(relation.items())))
    stringified_relation = json.dumps(minified_relation, sort_keys=True)
    generated_hash = hashlib.sha256(stringified_relation.encode("utf-8")).hexdigest()
    return generated_hash, stringified_relation


def merge_landscape_entities(
    base: dict,
    database: dict,
    database_index: int,
    schema: dict | None,
    schema_index: int,
    landscape_name: str,
    landscape_type: str,
    is_updating_landscape: bool,
) -> dict | None:
    """
    Merge multiple landscape entities into one
    """

    if is_updating_landscape:
        _log.debug("Updating existing entities")
    else:
        _log.debug("Merging entities")

    def get_entity_id(entity: dict) -> str:
        schema_string = f".{schema.get('name')}" if schema.get("name", None) else ""
        return f"{database.get('id')}{schema_string}.{entity.get('tableName')}"

    if not schema or schema.get("entities") is None or len(schema.get("entities")) == 0:
        _log.info("No entities to merge or replace")
        return base

    matching_entity_table_names = [
        get_entity_id(entity)
        for entity in schema.get("entities", [])
        if get_entity_id(entity)
        in [
            get_entity_id(base_entity)
            for base_entity in base.get("databases", [])[database_index].get("schemas", [])[schema_index].get("entities", [])
        ]
    ]

    for entity in schema.get("entities", []):
        if get_entity_id(entity) in matching_entity_table_names:
            matching_entity_in_base = next(
                i
                for i, base_entity in enumerate(
                    base.get("databases", [])[database_index].get("schemas", [])[schema_index].get("entities", [])
                )
                if get_entity_id(base_entity) == get_entity_id(entity)
            )

            if matching_entity_in_base is not None:
                if is_updating_landscape:
                    _log.debug(
                        f"Updating entity {entity.get('tableName')} within schema {schema.get('name')} under database {database.get('id')} from landscape {landscape_name} (from {landscape_type})."
                    )
                else:
                    _log.debug(
                        f"Entity {entity.get('tableName')} within schema {schema.get('name')} under database {database.get('id')} from landscape {landscape_name} (from {landscape_type}) already exists in the flattened landscape."
                    )
                    _log.debug(
                        f"Replacing entity {entity.get('tableName')} within schema {schema.get('name')} under database {database.get('id')} in the flattened landscape with entity from landscape {landscape_name} (from {landscape_type})."
                    )
                base["databases"][database_index]["schemas"][schema_index]["entities"][matching_entity_in_base] = entity
        else:
            if not is_updating_landscape:
                _log.debug(
                    f"Adding new entity {entity.get('tableName')} within schema {schema.get('name')} under database {database.get('id')} from landscape {landscape_name} (from {landscape_type})"
                )
            base["databases"][database_index]["schemas"][schema_index]["entities"].append(entity)
    return base


def merge_landscape_schemas(
    base: dict,
    database: dict | None,
    database_index: int,
    landscape_name: str,
    landscape_type: str,
    is_updating_landscape: bool,
) -> dict:
    """
    Merge multiple landscape schemas into one
    """

    if is_updating_landscape:
        _log.debug("Updating existing schemas")
    else:
        _log.debug("Merging schemas")

    def get_schema_string(schema: dict) -> str:
        schema_string = None
        if schema.get("name"):
            schema_string = schema.get("name")
            schema_string = f".{schema_string}" if schema_string else ""
        return f"{database.get('id')}{schema_string}"

    if database is None or database.get("schemas") is None or len(database.get("schemas")) == 0:
        _log.info("No schemas to merge")
        return base

    matching_schema_names = [
        get_schema_string(schema)
        for schema in database.get("schemas", [])
        if get_schema_string(schema)
        in [get_schema_string(base_schema) for base_schema in base.get("databases", [])[database_index].get("schemas", [])]
    ]

    for schema in database.get("schemas", []):
        if get_schema_string(schema) in matching_schema_names:
            matching_schema_index = next(
                i
                for i, base_schema in enumerate(base.get("databases")[database_index].get("schemas"))
                if get_schema_string(schema) == get_schema_string(base_schema)
            )
            if matching_schema_index is not None:
                if is_updating_landscape:
                    _log.debug(
                        f"Updating schema {schema.get('name')} under database {database.get('id')} from landscape {landscape_name} (from {landscape_type})."
                    )
                else:
                    _log.debug(
                        f"Schema {schema.get('name')} under database {database.get('id')} from landscape {landscape_name} (from {landscape_type}) already exists in the flattened landscape."
                    )
                base = merge_landscape_entities(
                    base=base,
                    database=database,
                    database_index=database_index,
                    schema=schema,
                    schema_index=matching_schema_index,
                    landscape_name=landscape_name,
                    landscape_type=landscape_type,
                    is_updating_landscape=is_updating_landscape,
                )
        else:
            if not is_updating_landscape:
                _log.debug(
                    f"Adding new schema {schema.get('name')} under database {database.get('id')} from landscape {landscape_name} (from {landscape_type})"
                )
            base["databases"][database_index]["schemas"].append(schema)

    return base


def merge_landscape_databases(
    base: dict, landscape: dict | None, landscape_name: str, landscape_type: str, is_updating_landscape: bool
) -> dict:
    """
    Merge multiple landscape databases into one
    """
    if is_updating_landscape:
        _log.debug("Updating existing databases")
    else:
        _log.debug("Merging databases")

    def get_database_string(database: dict) -> str:
        return f"{database.get('id')}"

    if landscape is None or landscape.get("databases") is None or len(landscape.get("databases")) == 0:
        _log.info("No databases to merge")
        return base

    matching_database_ids = [
        get_database_string(db)
        for db in landscape.get("databases", [])
        if get_database_string(db) in [get_database_string(base_db) for base_db in base.get("databases")]
    ]

    for database in landscape.get("databases", []):
        if get_database_string(database) in matching_database_ids:
            matching_database_index = next(
                i for i, base_db in enumerate(base.get("databases", [])) if get_database_string(base_db) == get_database_string(database)
            )
            if matching_database_index is not None:
                if is_updating_landscape:
                    _log.debug(
                        f"Updating database {get_database_string(database)} from landscape {landscape_name} (from {landscape_type})."
                    )
                else:
                    _log.debug(
                        f"Database {get_database_string(database)} from landscape {landscape_name} (from {landscape_type}) already exists in the flattened landscape."
                    )
                base = merge_landscape_schemas(
                    base=base,
                    database=database,
                    database_index=matching_database_index,
                    landscape_name=landscape_name,
                    landscape_type=landscape_type,
                    is_updating_landscape=is_updating_landscape,
                )
        else:
            if not is_updating_landscape:
                _log.debug(f"Adding new database {get_database_string(database)} from landscape {landscape_name} (from {landscape_type})")
            base["databases"].append(database)
    return base


def merge_landscape_relations(
    base: dict, landscape: dict | None, landscape_name: str, landscape_type: str, entity_ids: list[str], is_updating_landscape: bool
) -> dict:
    """
    Merge multiple landscape relations into one
    """

    if is_updating_landscape:
        _log.debug("Updating existing relations")
    else:
        _log.debug("Merging relations")

    if not landscape or landscape.get("relations") is None or len(landscape.get("relations")) == 0:
        _log.info("No relations to merge")
        return base

    relations = landscape.get("relations", [])

    def filter_precondition(relation: dict) -> tuple[bool, str]:
        if relation.get("type") == "entity-mapping-same-table":
            return relation.get("entity") in entity_ids, f"entity {relation.get('entity')} does not exist in the flattened landscape"

        is_source_entity_available = relation.get("source").get("id") in entity_ids
        is_target_entity_available = relation.get("target").get("id") in entity_ids

        reason = ""
        if not is_source_entity_available:
            reason = f"source entity {relation.get('source').get('id')} does not exist in the flattened landscape"
        if not is_target_entity_available:
            if reason:
                reason += " and "
            reason += f"target entity {relation.get('target').get('id')} does not exist in the flattened landscape"

        are_all_mapping_entities_available = True
        if len(relation.get("mapping", [])) > 0:
            filtered_available_mapping_entities = [
                mapping_entity.get("entity")
                for mapping_entity in list(filter(lambda mapping: mapping.get("entity") not in entity_ids, relation.get("mapping")))
            ]
            are_all_mapping_entities_available = len(filtered_available_mapping_entities) == 0
            if not are_all_mapping_entities_available:
                if reason:
                    reason += " and "
                reason += f"mapping {'entities' if len(filtered_available_mapping_entities) != 1 else 'entity'} {', '.join(filtered_available_mapping_entities)} {'do' if len(filtered_available_mapping_entities) != 1 else 'does'} not exist in the flattened landscape"
        return is_source_entity_available and is_target_entity_available and are_all_mapping_entities_available, reason

    filtered_relations = []
    omitted_relations = []

    for relation in relations:
        condition, reason = filter_precondition(relation)
        if condition:
            filtered_relations.append(relation)
        else:
            omitted_relations.append((relation, reason))

    for relation, reason in omitted_relations:
        relation_hash, stringified_relation = get_relation_string(relation)
        _log.warning(f"Omitting relation {stringified_relation} from landscape {landscape_name} (from {landscape_type}) because {reason}.")

    base_relation_hashes = [get_relation_string(base_relation)[0] for base_relation in base.get("relations", [])]
    matching_relation_hashes = []

    for relation in filtered_relations:
        relation_hash, stringified_relation = get_relation_string(relation)
        if relation_hash in base_relation_hashes:
            matching_relation_hashes.append(relation_hash)

    for relation in filtered_relations:
        relation_hash, stringified_relation = get_relation_string(relation)
        if relation_hash in matching_relation_hashes:
            matching_relation_index_in_base = next(
                i for i, base_relation_hash in enumerate(base_relation_hashes) if base_relation_hash == relation_hash
            )
            if matching_relation_index_in_base is not None:
                if is_updating_landscape:
                    _log.debug(f"Updating relation {stringified_relation} from landscape {landscape_name} (from {landscape_type}).")
                else:
                    _log.debug(
                        f"Relation {stringified_relation} from landscape {landscape_name} (from {landscape_type}) already exists in the flattened landscape."
                    )
                    _log.debug(
                        f"Replacing relation {stringified_relation} in the flattened landscape with relation in landscape {landscape_name} (from {landscape_type})."
                    )
                base["relations"][matching_relation_index_in_base] = relation
        else:
            if not is_updating_landscape:
                _log.debug(f"Adding new relation {stringified_relation} from landscape {landscape_name} (from {landscape_type})")
            base["relations"].append(relation)
    return base


def merge_landscape_idtypes(
    base: dict, landscape: dict | None, landscape_name: str, landscape_type: str, is_updating_landscape: bool
) -> dict:
    """
    Merge multiple landscape idtypes into one
    """

    if is_updating_landscape:
        _log.debug("Updating existing idtypes")
    else:
        _log.debug("Merging idtypes")

    if not landscape or landscape.get("idtypes") is None or len(landscape.get("idtypes")) == 0:
        _log.info("No idtypes to merge")
        return base

    matching_idtypes = [
        idtype.get("id")
        for idtype in landscape.get("idtypes", [])
        if idtype.get("id") in [base_idtype.get("id") for base_idtype in base.get("idtypes", [])]
    ]

    for idtype in landscape.get("idtypes", []):
        if idtype.get("id") in matching_idtypes:
            matching_idtype_index_in_base = next(
                i for i, base_idtype in enumerate(base.get("idtypes", [])) if base_idtype.get("id") == idtype.get("id")
            )
            if matching_idtype_index_in_base is not None:
                if is_updating_landscape:
                    _log.debug(f"Updating idtype {idtype.get('id')} from landscape {landscape_name} (from {landscape_type}).")
                else:
                    _log.debug(
                        f"Idtype {idtype.get('id')} from landscape {landscape_name} (from {landscape_type}) already exists in the flattened landscape."
                    )
                    _log.debug(
                        f"Replacing idtype {idtype.get('id')} in the flattened landscape with idtype from landscape {landscape_name} (from {landscape_type})."
                    )
                base["idtypes"][matching_idtype_index_in_base] = idtype
        else:
            if not is_updating_landscape:
                _log.debug(f"Adding new idtype {idtype.get('id')} from landscape {landscape_name} (from {landscape_type})")
            base["idtypes"].append(idtype)
    return base


def merge_landscape_dashboards(
    base: dict, landscape: dict | None, landscape_name: str, landscape_type: str, is_updating_landscape: bool
) -> dict:
    """
    Merge multiple landscape dashboards into one.
    """

    def log_action(action: str, dashboard_id: str):
        _log.debug(f"{action} dashboard {dashboard_id} from landscape {landscape_name} (from {landscape_type}).")

    def find_matching_dashboard_index(dashboard_id: str, dashboards: list[dict]) -> int | None:
        return next((i for i, d in enumerate(dashboards) if d.get("id") == dashboard_id), None)

    _log.debug("Updating existing dashboards" if is_updating_landscape else "Merging dashboards")

    if not landscape or not isinstance(landscape.get("dashboards"), list) or not landscape["dashboards"]:
        _log.info("No dashboards to merge")
        return base

    base.setdefault("dashboards", [])

    for dashboard in landscape["dashboards"]:
        dashboard_id = dashboard.get("id")
        if not dashboard_id:
            _log.warning(f"Skipping dashboard with missing ID in landscape {landscape_name} (from {landscape_type}).")
            continue

        matching_index = find_matching_dashboard_index(dashboard_id, base["dashboards"])

        if matching_index is not None:
            if is_updating_landscape:
                log_action("Updating", dashboard_id)
            else:
                log_action("Replacing", dashboard_id)
            base["dashboards"][matching_index] = dashboard
        else:
            if not is_updating_landscape:
                log_action("Adding new", dashboard_id)
            base["dashboards"].append(dashboard)

    return base


def merge_landscape_named_id_sets(
    base: dict, landscape: dict | None, landscape_name: str, landscape_type: str, entity_ids: list[str], is_updating_landscape: bool
) -> dict:
    """
    Merge multiple landscape named id sets into one
    """
    if is_updating_landscape:
        _log.debug("Updating existing named id sets")
    else:
        _log.debug("Merging named id sets")

    def get_custom_dataset_string(custom_dataset: dict, with_provider_type: bool = True) -> str:
        provider_type = ""
        database_id = ""
        schema_name = ""
        entity_id = ""
        if custom_dataset.get("providerType"):
            provider_type = custom_dataset.get("providerType")
            provider_type = f"{provider_type}" if provider_type else ""
        if custom_dataset.get("databaseId"):
            database_id = custom_dataset.get("databaseId")
            database_id = f".{database_id}" if with_provider_type else database_id if database_id else ""
        if custom_dataset.get("schemaName"):
            schema_name = custom_dataset.get("schemaName")
            schema_name = f".{schema_name}" if schema_name else ""
        if custom_dataset.get("entityId"):
            entity_id = custom_dataset.get("entityId")
            entity_id = f".{entity_id}" if entity_id else ""
        return f"{provider_type}{database_id}{schema_name}{entity_id}" if with_provider_type else f"{database_id}{schema_name}{entity_id}"

    if not landscape or landscape.get("namedIdSets") is None or len(landscape.get("namedIdSets")) == 0:
        _log.info("No named id sets to merge")
        return base

    custom_datasets = landscape.get("namedIdSets", [])

    filtered_custom_datasets = [
        custom_dataset for custom_dataset in custom_datasets if get_custom_dataset_string(custom_dataset, False) in entity_ids
    ]
    omitted_custom_datasets = [
        custom_dataset for custom_dataset in custom_datasets if get_custom_dataset_string(custom_dataset, False) not in entity_ids
    ]

    for custom_dataset in omitted_custom_datasets:
        _log.warning(
            f"Omitting custom dataset {get_custom_dataset_string(custom_dataset)} from landscape {landscape_name} (from {landscape_type}) because the entity {custom_dataset.get('entityId')} does not exist in the flattened landscape."
        )

    matching_custom_datasets = [
        get_custom_dataset_string(custom_dataset)
        for custom_dataset in filtered_custom_datasets
        if get_custom_dataset_string(custom_dataset)
        in [get_custom_dataset_string(base_named_id_set) for base_named_id_set in base.get("namedIdSets", [])]
    ]

    for custom_dataset in filtered_custom_datasets:
        if get_custom_dataset_string(custom_dataset) in matching_custom_datasets:
            matching_custom_dataset_index_in_base = next(
                i
                for i, base_custom_dataset in enumerate(base.get("namedIdSets", []))
                if get_custom_dataset_string(base_custom_dataset) == get_custom_dataset_string(custom_dataset)
            )
            if matching_custom_dataset_index_in_base is not None:
                if is_updating_landscape:
                    _log.debug(
                        f"Updating named id set {get_custom_dataset_string(custom_dataset)} from landscape {landscape_name} (from {landscape_type})."
                    )
                else:
                    _log.debug(
                        f"Named id set {get_custom_dataset_string(custom_dataset)} from landscape {landscape_name} (from {landscape_type}) already exists in the flattened landscape."
                    )
                    _log.debug(
                        f"Replacing custom dataset {get_custom_dataset_string(custom_dataset)} in the flattened landscape with the custom dataset from landscape {landscape_name} (from {landscape_type})."
                    )
                base["namedIdSets"][matching_custom_dataset_index_in_base] = custom_dataset
        else:
            if not is_updating_landscape:
                _log.debug(
                    f"Adding new named id set {get_custom_dataset_string(custom_dataset)} from landscape {landscape_name} (from {landscape_type}) in the flattened landscape."
                )
            base["namedIdSets"].append(custom_dataset)
    return base


def merge_landscape_dict(
    landscapes: list[dict],
    log_level: Literal["debug", "info", "warning", "error", "critical"] | None = "debug",
) -> dict | None:
    """
    Merge multiple landscape dicts into one
    """
    computed_log_level = LOG_LEVEL_DICT.get(log_level.lower(), logging.WARNING) if log_level is not None else logging.WARNING
    current_level = _log.getEffectiveLevel()
    _log.setLevel(level=computed_log_level)

    if not landscapes:
        _log.info("No landscapes to merge")
        return None

    is_updating_landscape = len({landscape.get("name") for landscape in landscapes}) == 1

    if is_updating_landscape:
        _log.info(f"Updating landscape: {landscapes[0].get('name')}")
    else:
        _log.info("Merging landscapes")

    file_landscapes = [landscape for landscape in landscapes if landscape.get("type") == "file"]
    db_landscapes = [landscape for landscape in landscapes if landscape.get("type") != "file"]

    filtered_file_landscapes = [
        file_landscape
        for file_landscape in file_landscapes
        if file_landscape.get("name") not in [db_landscape.get("name") for db_landscape in db_landscapes]
    ]

    filtered_landscapes = filtered_file_landscapes + db_landscapes

    landscapes_to_merge = [f"{ls.get('name')} (from {ls.get('type')})" for ls in filtered_landscapes]
    _log.debug(f"Landscapes to merge: {', '.join(landscapes_to_merge)}")

    base_landscape_object = {
        "name": "base",
        "type": None,
        "json_obj": {"databases": [], "relations": [], "idtypes": [], "namedIdSets": []},
    }
    base_landscape = base_landscape_object.get("json_obj")
    base_landscape_name = base_landscape_object.get("name")
    base_landscape_type = base_landscape_object.get("type")
    if not is_updating_landscape:
        _log.debug(f"Using {base_landscape_name} (from {base_landscape_type}) as the base landscape")

    landscape_names = [f"{base_landscape_name}"]
    if not is_updating_landscape:
        _log.debug(f"The flattened landscape currently contains these landscapes: {', '.join(landscape_names)}")

    for landscape_object in filtered_landscapes:
        landscape = landscape_object.get("json_obj", None)
        landscape_name = landscape_object.get("name", None)
        landscape_type = landscape_object.get("type", None)
        _log.info(f"Merging idtypes of landscape {landscape_object.get('name')} (from {landscape_type}) into the flattened landscape.")
        base_landscape = merge_landscape_idtypes(
            base=base_landscape,
            landscape=landscape,
            landscape_name=landscape_name,
            landscape_type=landscape_type,
            is_updating_landscape=is_updating_landscape,
        )
        if is_updating_landscape:
            _log.info(f"Updating idtypes of landscape {landscape_name} (from {landscape_type})")
        else:
            _log.debug(
                f"The idtypes of landscape {landscape_name} (from {landscape_type}) merged into the flattened landscape successfully!"
            )
            landscape_names.append(f"{landscape_name} (from {landscape_type})")
            _log.debug(f"The flattened landscape contains idtypes from these landscapes: {', '.join(landscape_names)}")

    if is_updating_landscape:
        _log.info(f"The idtypes of landscape {landscape_names[0]} updated successfully!")
    else:
        _log.info("All the idtypes across all the landscapes merged successfully!")

    idtypes = [idtype.get("id") for idtype in base_landscape.get("idtypes", [])]

    landscape_names = [f"{base_landscape_name}"]
    if not is_updating_landscape:
        _log.debug(f"The flattened landscape currently contains idtypes from these landscapes: {', '.join(landscape_names)}")

    for landscape_object in filtered_landscapes:
        landscape = landscape_object.get("json_obj", None)
        landscape_name = landscape_object.get("name", None)
        landscape_type = landscape_object.get("type", None)
        _log.info(f"Merging dashboards of landscape {landscape_object.get('name')} (from {landscape_type}) into the flattened landscape.")
        base_landscape = merge_landscape_dashboards(
            base=base_landscape,
            landscape=landscape,
            landscape_name=landscape_name,
            landscape_type=landscape_type,
            is_updating_landscape=is_updating_landscape,
        )
        if is_updating_landscape:
            _log.info(f"Updating dashboards of landscape {landscape_name} (from {landscape_type})")
        else:
            _log.debug(
                f"The dashboards of landscape {landscape_name} (from {landscape_type}) merged into the flattened landscape successfully!"
            )
            landscape_names.append(f"{landscape_name} (from {landscape_type})")
            _log.debug(f"The flattened landscape contains dashboards from these landscapes: {', '.join(landscape_names)}")

    if is_updating_landscape:
        _log.info(f"The dashboards of landscape {landscape_names[0]} updated successfully!")
    else:
        _log.info("All the dashboards across all the landscapes merged successfully!")

    landscape_names = [f"{base_landscape_name}"]
    for landscape_object in filtered_landscapes:
        landscape = landscape_object.get("json_obj", None)
        landscape_name = landscape_object.get("name", None)
        landscape_type = landscape_object.get("type", None)
        _log.info(f"Merging entities of landscape {landscape_object.get('name')} (from {landscape_type}) into the flattened landscape.")
        base_landscape = merge_landscape_databases(
            base=base_landscape,
            landscape=landscape,
            landscape_name=landscape_name,
            landscape_type=landscape_type,
            is_updating_landscape=is_updating_landscape,
        )
        if is_updating_landscape:
            _log.info(f"Updating entities of landscape {landscape_name} (from {landscape_type})")
        else:
            _log.debug(
                f"The entities of landscape {landscape_name} (from {landscape_type}) merged into the flattened landscape successfully!"
            )
            landscape_names.append(f"{landscape_name} (from {landscape_type})")
            _log.debug(f"The flattened landscape contains entities from these landscapes: {', '.join(landscape_names)}")

    if is_updating_landscape:
        _log.info(f"The entities of landscape {landscape_names[0]} updated successfully!")
    else:
        _log.info("All the entities across all the landscapes merged successfully!")

    entity_ids = []

    for db in base_landscape.get("databases", []):
        db_id = db.get("id")
        for schema in db.get("schemas", []):
            schema_name = schema.get("name")
            for entity in schema.get("entities", []):
                entity_table_name = entity.get("tableName")
                entity_id = f"{db_id}.{schema_name}.{entity_table_name}" if schema_name else f"{db_id}.{entity_table_name}"
                for column in entity.get("columns", []):
                    if column.get("idtype") is not None and column.get("idtype") not in idtypes:
                        _log.warning(
                            f"ID type {column.get('idtype')} for column {column.get('label') or column.get('id') or column.get('columnName')} in entity {entity_id} does not exist in the flattened landscape."
                        )
                entity_ids.append(entity_id)

    landscape_names = [f"{base_landscape_name}"]
    for landscape_object in filtered_landscapes:
        landscape = landscape_object.get("json_obj", None)
        landscape_name = landscape_object.get("name", None)
        landscape_type = landscape_object.get("type", None)
        _log.info(
            f"Merging relations, custom datasets and app config of {landscape_object.get('name')} (from {landscape_type}) into the flattened landscape."
        )
        base_landscape = merge_landscape_relations(
            base=base_landscape,
            landscape=landscape,
            landscape_name=landscape_name,
            landscape_type=landscape_type,
            entity_ids=entity_ids,
            is_updating_landscape=is_updating_landscape,
        )
        base_landscape = merge_landscape_named_id_sets(
            base=base_landscape,
            landscape=landscape,
            landscape_name=landscape_name,
            landscape_type=landscape_type,
            entity_ids=entity_ids,
            is_updating_landscape=is_updating_landscape,
        )
        if is_updating_landscape:
            _log.info(f"Updating landscape {landscape_name} (from {landscape_type})")
        else:
            _log.debug(f"Landscape {landscape_name} (from {landscape_type}) fully merged into the flattened landscape successfully!")
            landscape_names.append(f"{landscape_name} (from {landscape_type})")
            _log.debug(f"Landscapes currently fully merged in the flattened landscape: {', '.join(landscape_names)}")

    if is_updating_landscape:
        _log.info(f"Landscape {landscape_names[0]} updated successfully!")
    else:
        _log.info("All the landscapes merged successfully!")

    _log.setLevel(current_level)

    return {"json_obj": base_landscape}
