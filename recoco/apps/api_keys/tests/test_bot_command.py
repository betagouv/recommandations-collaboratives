from io import StringIO

import pytest
from django.contrib.auth.models import User
from django.core.management import CommandError, call_command
from model_bakery import baker

from ..models import ServiceAPIKey


def run(*args):
    out = StringIO()
    call_command("bot", *args, stdout=out)
    return out.getvalue().strip().splitlines()[-1]


@pytest.mark.django_db
def test_create_bot_with_a_key(current_site):
    key = run("create", "--name", "svc-bot", "--site", current_site.domain)

    bot = User.objects.get(username="svc-bot")
    assert bot.profile.is_bot
    assert not bot.has_usable_password()
    assert current_site in bot.profile.sites.all()
    api_key = ServiceAPIKey.objects.get(user=bot)
    assert api_key.site == current_site
    assert ServiceAPIKey.objects.get_from_key(key) == api_key


@pytest.mark.django_db
def test_create_requires_a_known_site():
    with pytest.raises(CommandError):
        run("create", "--name", "svc-bot")
    with pytest.raises(CommandError):
        run("create", "--name", "svc-bot", "--site", "unknown.example.org")
    assert not User.objects.filter(username="svc-bot").exists()


@pytest.mark.django_db
def test_create_refuses_existing_username(current_site):
    baker.make(User, username="taken")

    with pytest.raises(CommandError):
        run("create", "--name", "taken", "--site", current_site.domain)

    assert not ServiceAPIKey.objects.exists()


@pytest.mark.django_db
def test_renew_replaces_the_key(current_site):
    old_key = run("create", "--name", "svc-bot", "--site", current_site.domain)

    new_key = run("renew", "--name", "svc-bot")

    assert new_key != old_key
    bot = User.objects.get(username="svc-bot")
    assert bot.api_keys.count() == 1
    assert ServiceAPIKey.objects.get_from_key(new_key).site == current_site
    with pytest.raises(ServiceAPIKey.DoesNotExist):
        ServiceAPIKey.objects.get_from_key(old_key)


@pytest.mark.django_db
def test_delete_removes_bot_and_keys(current_site):
    run("create", "--name", "svc-bot", "--site", current_site.domain)

    run("delete", "--name", "svc-bot")

    assert not User.objects.filter(username="svc-bot").exists()
    assert not ServiceAPIKey.objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("action", ["renew", "delete"])
def test_renew_and_delete_never_touch_human_users(action):
    human = baker.make(User, username="human")

    with pytest.raises(CommandError):
        run(action, "--name", "human")

    assert User.objects.filter(pk=human.pk).exists()
