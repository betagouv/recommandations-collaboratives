from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from recoco.apps.api_keys.models import ServiceAPIKey


class Command(BaseCommand):
    help = (
        "Crée un compte de service et sa clé d'API pour un site donné. "
        "La clé n'est affichée qu'une seule fois."
    )

    def add_arguments(self, parser):
        parser.add_argument("username", help="nom du compte de service, ex: svc-grist")
        parser.add_argument(
            "--site", required=True, help="domaine du site, ex: recoco.beta.gouv.fr"
        )
        parser.add_argument(
            "--name", default=None, help="libellé de la clé, 50 caractères max"
        )
        parser.add_argument("--email", default="", help="email de contact du compte")

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"]
        domain = options["site"]
        name = options["name"] or username

        if len(name) > 50:
            raise CommandError("Le libellé de la clé dépasse 50 caractères.")

        try:
            site = Site.objects.get(domain=domain)
        except Site.DoesNotExist as exc:
            raise CommandError(f"Aucun site avec le domaine '{domain}'.") from exc

        if auth_models.User.objects.filter(username=username).exists():
            raise CommandError(f"L'utilisateur '{username}' existe déjà.")

        user = auth_models.User.objects.create(
            username=username, email=options["email"]
        )
        user.set_unusable_password()
        user.save()
        user.profile.sites.add(site)

        _, key = ServiceAPIKey.objects.create_key(name=name, user=user, site=site)

        self.stdout.write(
            self.style.SUCCESS(f"Compte de service '{username}' créé sur {domain}.")
        )
        self.stdout.write(f"Clé d'API : {key}")
        self.stdout.write(
            self.style.WARNING("Notez-la maintenant, elle ne sera plus affichée.")
        )
