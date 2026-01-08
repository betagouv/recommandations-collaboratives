import csv

from django.core.management import BaseCommand

from recoco.apps.resources.models import Resource


class Command(BaseCommand):
    help = "Check reminders and perform necessary actions"

    def add_arguments(self, parser):
        parser.add_argument(
            "input_file",
            type=str,
            help="Path of the csv file to import",
        )
        parser.add_argument(
            "--id", type=str, help="Column header to pk values", default="pk"
        )
        parser.add_argument(
            "--orga",
            type=str,
            help="Column header to support_orga values",
            default="support_orga",
        )

    def import_support_orga(self, input_file, id_key, orga_key):
        self.stdout.write("Checking reminders NEW_RECO ...")
        batch = []
        with open(input_file, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            if id_key not in reader.fieldnames:
                self.stderr.write(f"{id_key} not in headers")
                return 1
            if orga_key not in reader.fieldnames:
                self.stderr.write(f"{orga_key} not in headers")
                return 1
            for row in reader:
                orga = row[orga_key].strip()
                if orga == "-" or orga == "":
                    continue
                r = Resource.objects.filter(pk=int(row[id_key])).first()
                if r is None:
                    continue
                batch.append(r)
                r.support_orga = orga
            Resource.objects.bulk_update(batch, ["support_orga"], 100)

        self.stdout.write("Reminders check complete.")
        return 0

    def handle(self, *args, **kwargs):
        self.import_support_orga(
            kwargs["input_file"], id_key=kwargs["id"], orga_key=kwargs["orga"]
        )
