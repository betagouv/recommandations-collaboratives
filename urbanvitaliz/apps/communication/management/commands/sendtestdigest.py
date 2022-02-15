# encoding: utf-8

"""
Management command to send pending notifications as digests

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-01-24 22:39:27 CEST
"""


import json

from django.core.management.base import BaseCommand
from urbanvitaliz.apps.communication.api import send_in_blue_email
from urbanvitaliz.apps.communication.models import EmailTemplate


class Command(BaseCommand):
    help = "Send pending notifications as email digests"

    def handle(self, *args, **options):
        self.send_test_digest(*args, **options)

    def add_arguments(self, parser):
        parser.add_argument(
            "template_name", type=str, help="The name of the template, in DB"
        )
        parser.add_argument(
            "payload_file",
            type=str,
            help="A path where to find the JSON payload",
        )
        parser.add_argument("to", nargs="+", type=str)

    def send_test_digest(self, *args, **options):
        try:
            template = EmailTemplate.objects.get(name=options["template_name"])
        except EmailTemplate.DoesNotExist:
            print("This email template doesn't exist, aborting")
            exit(1)

        payload = {}
        with open(options["payload_file"], "r") as fd:
            payload = json.loads(fd.read())

        recipients = [{"name": "??", "email": email} for email in options["to"]]

        if send_in_blue_email(template.name, recipients, params=payload):
            print("Email sent! :)")
        else:
            print("Something went wrong! :(")


# eof
