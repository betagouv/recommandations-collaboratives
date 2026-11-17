import uuid

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from recoco.apps.api_keys.models import ServiceAPIKey


class Command(BaseCommand):
    help = (
        "Manage bot accounts and their API key: "
        "create a bot with a key, renew its key (revoking the previous ones), "
        "or delete the bot"
    )

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["create", "renew", "delete"])
        parser.add_argument("--name", required=True, help="Username of the bot")
        parser.add_argument(
            "--site",
            help="Domain of the site the key gives access to (create only)",
        )

    def handle(self, action, name, site=None, **options):
        with transaction.atomic():
            getattr(self, action)(name, site)

    def create(self, name, site_domain):
        if not site_domain:
            raise CommandError("--site is required to create a bot")
        try:
            site = Site.objects.get(domain=site_domain)
        except Site.DoesNotExist as exc:
            raise CommandError(f"Unknown site: {site_domain}") from exc
        if User.objects.filter(username=name).exists():
            raise CommandError(f"A user named {name!r} already exists")

        user = User.objects.create_user(username=name)  # unusable password
        user.profile.is_bot = True
        user.profile.save()
        user.profile.sites.add(site)

        self._issue_key(user, site)

    def renew(self, name, _site_domain):
        user = self._get_bot(name)
        # most recent key, revoked or not, tells which site to renew for
        api_key = user.api_keys.select_related("site").order_by("-created").first()
        if api_key is None:
            raise CommandError(f"Bot {name!r} has no API key to renew")

        site = api_key.site
        # revoke rather than delete, to keep a trace of past keys
        user.api_keys.filter(revoked=False).update(revoked=True)
        self._issue_key(user, site)

    def delete(self, name, _site_domain):
        user = self._get_bot(name)
        user.delete()  # cascades to its API keys
        self.stdout.write(self.style.SUCCESS(f"Bot {name!r} deleted"))

    def _get_bot(self, name):
        try:
            return User.objects.get(username=name, profile__is_bot=True)
        except User.DoesNotExist as exc:
            raise CommandError(f"No bot named {name!r}") from exc

    @staticmethod
    def _key_name(user):
        """<username>-<random id>, so each key of a bot gets a distinct name"""
        suffix = uuid.uuid4().hex[:8]
        max_length = ServiceAPIKey._meta.get_field("name").max_length
        return f"{user.username[: max_length - len(suffix) - 1]}-{suffix}"

    def _issue_key(self, user, site):
        _, key = ServiceAPIKey.objects.create_key(
            name=self._key_name(user), user=user, site=site
        )
        self.stdout.write(
            self.style.SUCCESS(f"API key for {user.username!r} on {site.domain}:")
        )
        # alone on its own line so it can be piped; shown only once
        self.stdout.write(key)
