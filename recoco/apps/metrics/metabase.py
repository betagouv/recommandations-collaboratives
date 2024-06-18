import ast
import re

from django.conf import settings
from metabase_api import Metabase_API


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
    table_ids = {}
    table_results = mb.get("/api/table/")
    for table in table_results:
        schema = table["schema"]

        if schema not in table_ids:
            table_ids[schema] = {}

        table_ids[schema][table["name"]] = table["id"]

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
    cards_old_vs_new_ids = {}
    for source_card in source_cards["data"]:
        # get needed card data like table_id
        source_card_data = mb.get_item_info("card", source_card["id"])

        # TODO: can be optimized by calling only once per table with cache
        table_source = mb.get(f"/api/table/{source_card_data['table_id']}")
        table_name = table_source["name"]
        new_card = clone_card(
            mb=mb,
            db_id=table_source["db_id"],
            card_id=source_card["id"],
            table_name=table_name,
            source_schema=table_source["schema"],
            source_table_id=source_card_data["table_id"],
            target_schema=target_schema,
            target_table_id=table_ids[target_schema][table_name],
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
    db_id: int,
    card_id: int,
    table_name: str,
    source_schema: str,
    source_table_id: int,
    target_schema: str,
    target_table_id: int,
    new_card_collection_id: int,
):
    """Rewrite metabase-api method to support multi schema and safer ast.literal_eval

    Args:
        mb (Metabase_API): Metabase Client
        db_id (int): database id
        card_id (int): id of card to duplicate
        table_name (str): the name of the table concerned by the card
        source_schema (str): the name of source database schema
        source_table_id (int): id of table used in source card
        target_schema (str): the name of target database schema
        target_table_id (int): id of table to set in target card
        new_card_collection_id (int): id of collection to used in new card
    """
    card_info = mb.get_item_info("card", card_id)

    # fetch fields to create col name and id mapping
    fields = mb.get(f"/api/database/{db_id}/fields")
    target_table_col_name_id_mapping = {
        i["name"]: i["id"]
        for i in fields
        if i["table_name"] == table_name and i["schema"] == target_schema
    }
    source_table_col_id_name_mapping = {
        i["id"]: i["name"]
        for i in fields
        if i["table_name"] == table_name and i["schema"] == source_schema
    }

    query_data = card_info["dataset_query"]["query"]

    # change the underlying table for the card
    query_data["source-table"] = target_table_id

    # :( transform to string so it is easier to replace the column IDs
    query_data_str = str(query_data)

    res = re.findall("\['field', .*?\]", query_data_str)
    source_column_IDs = [ast.literal_eval(i)[1] for i in res]

    # replace column IDs from old table with the column IDs from new table
    for source_col_id in source_column_IDs:
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
