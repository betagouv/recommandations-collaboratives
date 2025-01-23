import ast
import re

from django.conf import settings
from metabase_api import Metabase_API

table_ids = {}
table_names = {}
cards_old_vs_new_ids = {}


def clone_collection(
    source_collection_id: int, new_collection_name: str, target_schema: str
):

    # https://pypi.org/project/metabase-api/
    # https://www.metabase.com/docs/latest/api-documentation
    # authentication using API key (is_admin=False is set to avoid friendly table name alert)
    mb = Metabase_API(
        settings.METABASE_HOST, api_key=settings.METABASE_API_KEY, is_admin=False
    )

    # fetch table to create dict with table ids per schema
    table_results = mb.get("/api/table/")
    for table in table_results:
        schema = table["schema"]

        if schema not in table_ids:
            table_ids[schema] = {}
            table_names[schema] = {}

        table_ids[schema][table["name"]] = table["id"]
        table_names[schema][table["id"]] = table["name"]

    # fetch source dashboard to get dashcards info
    dashboards = mb.get(
        f"/api/collection/{source_collection_id}/items?models=dashboard"
    )
    source_dashboard_data = mb.get_item_info("dashboard", dashboards["data"][0]["id"])

    # create new collection
    new_collection = mb.create_collection(
        new_collection_name, parent_collection_name="Root", return_results=True
    )

    # duplicate cards from source collection to new one
    source_cards = mb.get(f"/api/collection/{source_collection_id}/items?models=card")

    # sort by id to prevent the cloned card from depending on another card that has not yet been created
    source_cards_data = sorted(source_cards["data"], key=lambda x: x["id"])

    for source_card in source_cards_data:
        # get needed card data like table_id
        source_card_data = mb.get_item_info("card", source_card["id"])
        if source_card_data["table_id"]:
            # TODO: can be optimized by calling only once per table with cache
            table_source = mb.get(f"/api/table/{source_card_data['table_id']}")
            table_name = table_source["name"]
            new_card = clone_card(
                mb=mb,
                card_info=source_card_data,
                table_name=table_name,
                source_schema=table_source["schema"],
                target_schema=target_schema,
                new_card_collection_id=new_collection["id"],
            )
        else:
            # it is a card with SQL query
            new_card = clone_card_native_query(
                mb=mb,
                card_info=source_card_data,
                source_schema=table_source[
                    "schema"
                ],  # FIXME: :( takes the schema of the last lopp
                target_schema=target_schema,
                new_card_collection_id=new_collection["id"],
            )

        # keep ids mapping to get dashcard info
        cards_old_vs_new_ids[source_card["id"]] = new_card["id"]

    # create new dashboard
    new_dashboard_data = {
        "name": new_collection_name,  # same name as collection
        "collection_id": new_collection["id"],
    }
    new_dashboard = mb.post("/api/dashboard/", json=new_dashboard_data)

    dashcards = []
    for dashcard in source_dashboard_data["dashcards"]:

        # init new card with id card switch
        new_dashcard = {
            "id": -1,
            "card_id": cards_old_vs_new_ids[dashcard["card_id"]],
        }
        # add same position keys
        for key_to_duplicate in [
            "visualization_settings",
            "size_x",
            "size_y",
            "col",
            "row",
            "parameter_mappings",
        ]:
            new_dashcard[key_to_duplicate] = dashcard[key_to_duplicate]
        dashcards.append(new_dashcard)

        # dashcard creation need to send one by one with id -1
        res_dashcard_creation = mb.put(
            f"/api/dashboard/{new_dashboard['id']}",
            "raw",
            json={"id": new_dashboard["id"], "dashcards": dashcards},
        )
        if res_dashcard_creation.ok:
            dashcard_creation = res_dashcard_creation.json()
            dashcards = dashcard_creation["dashcards"]


def clone_card(
    mb: Metabase_API,
    card_info: dict,
    table_name: str,
    source_schema: str,
    target_schema: str,
    new_card_collection_id: int,
):
    """Rewrite metabase-api method to support multi schema and safer ast.literal_eval

    Args:
        mb (Metabase_API): Metabase Client
        card_info (dict): data about card return by Metabase_API.get_item_info()
        table_name (str): the name of the table concerned by the card
        source_schema (str): the name of source database schema
        target_schema (str): the name of target database schema
        new_card_collection_id (int): id of collection to used in new card
    """
    query_data = card_info["dataset_query"]["query"]

    # change the underlying table for the card
    target_table_names = [table_name]

    source_table = query_data["source-table"]
    if isinstance(source_table, str) and source_table.startswith("card__"):
        # card from a saved card instead a source table
        card_source_id = int(query_data["source-table"].replace("card__", ""))
        query_data["source-table"] = f"card__{cards_old_vs_new_ids[card_source_id]}"
    else:
        try:
            query_data["source-table"] = table_ids[target_schema][table_name]
        except KeyError as e:
            print("Unable to find target_schema, available: ", table_ids.keys())
            raise e

    if "joins" in query_data:
        for join in query_data["joins"]:
            join_table_name = table_names[source_schema][join["source-table"]]
            target_table_names.append(join_table_name)
            join["source-table"] = table_ids[target_schema][join_table_name]

    # :( transform to string so it is easier to replace the column IDs
    query_data_str = str(query_data)

    # fetch fields to create col name and id mapping
    fields = mb.get(f"/api/database/{card_info['database_id']}/fields")
    target_table_col_name_id_mapping = {
        i["name"]: i["id"]
        for i in fields
        if i["table_name"] in target_table_names and i["schema"] == target_schema
    }
    source_table_col_id_name_mapping = {
        i["id"]: i["name"]
        for i in fields
        if i["table_name"] in target_table_names and i["schema"] == source_schema
    }

    res = re.findall(
        "\['field', .*?\]", query_data_str
    )  # FIXME: Escape sequence is wrong!
    source_column_IDs = [ast.literal_eval(i)[1] for i in res]

    # replace column IDs from old table with the column IDs from new table
    for source_col_id in source_column_IDs:
        if isinstance(source_col_id, int):
            source_col_name = source_table_col_id_name_mapping[source_col_id]
            target_col_id = target_table_col_name_id_mapping[source_col_name]
            query_data_str = query_data_str.replace(
                "['field', {}, ".format(source_col_id),
                "['field', {}, ".format(target_col_id),
            )

    card_info["dataset_query"]["query"] = ast.literal_eval(query_data_str)

    new_card_json = {}
    for key in ["dataset_query", "display", "visualization_settings"]:
        new_card_json[key] = card_info[key]

    new_card_json["name"] = card_info["name"]
    new_card_json["collection_id"] = new_card_collection_id

    return mb.create_card(custom_json=new_card_json, verbose=True, return_card=True)


def clone_card_native_query(
    mb: Metabase_API,
    card_info: dict,
    source_schema: str,
    target_schema: str,
    new_card_collection_id: int,
):
    """Rewrite metabase-api method to simplify for SQL query card

    Args:
        mb (Metabase_API): Metabase Client
        card_info (dict): data about card return by Metabase_API.get_item_info()
        source_schema (str): the name of source database schema
        source_table_id (int): id of table used in source card
        new_card_collection_id (int): id of collection to used in new card
    """

    native_query = card_info["dataset_query"]["native"]["query"]
    native_query = native_query.replace(f'"{source_schema}"', f'"{target_schema}"')
    card_info["dataset_query"]["native"]["query"] = native_query

    new_card_json = {}
    for key in ["dataset_query", "display", "visualization_settings"]:
        new_card_json[key] = card_info[key]

    new_card_json["name"] = card_info["name"]
    new_card_json["collection_id"] = new_card_collection_id

    return mb.create_card(custom_json=new_card_json, verbose=True, return_card=True)
