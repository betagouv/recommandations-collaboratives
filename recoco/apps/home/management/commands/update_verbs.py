import csv

from django.core.management import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Reads a csv containing changes to apply to verbs in existing notifications and actions"
    temp_table_name = "temp-verb-mapping"

    def add_arguments(self, parser):
        parser.add_argument(
            "matching_path",
            help="Path to csv containing matching between old string and verb name. Must contain columns 'old' and 'new'. Be careful to escape separators",
        )

    def parse_matching(self, matching_path):
        matching = []
        with open(matching_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                matching.append(
                    {
                        "old": row["old"].replace("'", "''"),
                        "new": row["new"].replace("'", "''"),
                    }
                )
        return matching

    def save_matching(self, matching):
        query = (  # noqa: S608
            "INSERT INTO verb_mapping (old, new) VALUES \n"  # noqa: S608
            + ",\n".join(f"('{row['old']}', '{row['new']}')" for row in matching)  # noqa: S608 need access to server to be a pb
            + ";"  # noqa: S608
        )  # noqa: S608

        with connection.cursor() as cursor:
            cursor.execute("BEGIN;")
            self.stdout.write("create temp table")
            cursor.execute("CREATE TEMP TABLE verb_mapping (old VARCHAR, new VARCHAR);")
            self.stdout.write("filling temp table with requested verb updates")
            cursor.execute(query)

    def update_verbs(self):
        query_notifs = """
                       -- apply the mapping to notification verbs

                       UPDATE notifications_notification AS notif
                       SET verb = mapping.new FROM verb_mapping mapping
                       WHERE notif.verb = mapping.old; \
                       """
        query_actions = """
                        -- apply the mapping to action verbs

                        UPDATE actstream_action AS action
                        SET verb = mapping.new
                        FROM verb_mapping mapping
                        WHERE action.verb = mapping.old;
                        """

        with connection.cursor() as cursor:
            self.stdout.write("updating notif verbs")
            cursor.execute(query_notifs)
            self.stdout.write("updating action verbs")
            cursor.execute(query_actions)

    def display_all_verbs_to_check(self):
        query = """
                WITH all_verbs AS (SELECT DISTINCT verb
                                   FROM notifications_notification
                                   UNION
                                   SELECT DISTINCT verb
                                   FROM actstream_action)
                SELECT DISTINCT verb
                FROM all_verbs
                ORDER BY verb;
                """

        self.stdout.write("listing all current verbs - to check with verbs.py")
        with connection.cursor() as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                self.stdout.write(row[0])
        input("Press ENTER to continue")

    def clean_temp_db_and_commit(self):
        with connection.cursor() as cursor:
            self.stdout.write("drop temp table")
            cursor.execute("DROP TABLE verb_mapping ;")
            self.stdout.write("commit changes")
            cursor.execute("COMMIT ;")

    def update(self, matching):
        self.save_matching(matching)
        self.update_verbs()
        self.display_all_verbs_to_check()
        self.clean_temp_db_and_commit()

    def handle(self, *args, **options):
        matching_path = options["matching_path"]
        matching = self.parse_matching(matching_path)
        self.update(matching)
