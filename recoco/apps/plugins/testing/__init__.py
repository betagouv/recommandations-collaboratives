from django.db import connection

# Label of the plugin app installed in test settings only
PLUGIN = "plugin_testapp"


def current_search_path(conn=connection):
    with conn.cursor() as cursor:
        cursor.execute("SHOW search_path")
        return cursor.fetchone()[0].replace(" ", "").split(",")
