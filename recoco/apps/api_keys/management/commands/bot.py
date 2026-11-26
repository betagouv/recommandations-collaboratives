import uuid

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from recoco.apps.api_keys.models import ServiceAPIKey
from recoco.apps.home.utils import deactivate_user, reactivate_user


class Command(BaseCommand):
    help = (
        "Manage bot accounts and their API keys, one key per site: "
        "create a bot with a key for a site, or give an existing bot a key "
        "for another site; renew the key of a site (revoking the previous one); "
        "disable the bot (deactivating it and revoking all its keys); "
        "or enable a disabled bot again with a new key for a site. "
        "After enabling, renew the bot's other sites one by one. "
        "A disabled bot keeps its groups and permissions, "
        "and gets them back when enabled."
    )

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["create", "renew", "disable", "enable"])
        parser.add_argument("--name", required=True, help="Username of the bot")
        parser.add_argument(
            "--site",
            help="Domain of the site the key gives access to (all but disable)",
        )

    def handle(self, action, name, site=None, **options):
        with transaction.atomic():
            if action == "disable":
                self.disable(name)
            else:
                getattr(self, action)(name, self._get_site(action, site))

    def create(self, name, site):
        user = User.objects.filter(username=name).first()
        if user is None:
            user = User.objects.create_user(username=name)  # unusable password
            user.profile.is_bot = True
            user.profile.save()
        elif not user.profile.is_bot:
            raise CommandError(f"A user named {name!r} already exists")
        elif not user.is_active:
            raise CommandError(f"Bot {name!r} is disabled, use enable")
        elif user.api_keys.filter(site=site, revoked=False).exists():
            raise CommandError(
                f"Bot {name!r} already has a key for {site.domain}, use renew"
            )

        user.profile.sites.add(site)
        self._issue_key(user, site)

    def renew(self, name, site):
        user = self._get_bot(name)
        if not user.is_active:
            raise CommandError(f"Bot {name!r} is disabled")
        self._check_had_key(user, site, "renew")

        self._revoke_keys(user, site)
        self._issue_key(user, site)

    def disable(self, name):
        # deactivate rather than delete: keeps what the bot created
        user = self._get_bot(name)
        if not user.is_active:
            raise CommandError(f"Bot {name!r} is already disabled")
        deactivate_user(user)
        self._revoke_keys(user)
        self.stdout.write(self.style.SUCCESS(f"Bot {name!r} disabled"))

    def enable(self, name, site):
        user = self._get_bot(name)
        if user.is_active:
            raise CommandError(f"Bot {name!r} is not disabled")
        if user.profile.deleted:
            raise CommandError(f"Bot {name!r} is deleted and cannot be enabled")
        self._check_had_key(user, site, "enable it with")

        reactivate_user(user)
        # a key left usable by hand on any site must not survive the enable
        self._revoke_keys(user)
        self._issue_key(user, site)

    def _get_site(self, action, domain):
        if not domain:
            raise CommandError(f"--site is required to {action} a bot")
        try:
            return Site.objects.get(domain=domain)
        except Site.DoesNotExist as exc:
            raise CommandError(f"Unknown site: {domain}") from exc

    def _get_bot(self, name):
        try:
            return User.objects.get(username=name, profile__is_bot=True)
        except User.DoesNotExist as exc:
            raise CommandError(f"No bot named {name!r}") from exc

    def _check_had_key(self, user, site, action):
        """A key is renewed or enabled only on a site the bot already had one
        for (revoked or not): giving it a new site is create's job."""
        if not user.api_keys.filter(site=site).exists():
            raise CommandError(
                f"Bot {user.username!r} has no API key for {site.domain} to "
                f"{action}, use create"
            )

    @staticmethod
    def _revoke_keys(user, site=None):
        # revoke rather than delete, to keep a trace of past keys
        keys = user.api_keys.filter(revoked=False)
        if site is not None:
            keys = keys.filter(site=site)
        keys.update(revoked=True)

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
