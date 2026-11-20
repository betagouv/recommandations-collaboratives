from io import StringIO

import pytest
from django.contrib.auth.models import User
from django.core.management import CommandError, call_command
from model_bakery import baker

from recoco.apps.home.utils import deactivate_user

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
def test_renew_revokes_the_old_key(current_site):
    old_key = run("create", "--name", "svc-bot", "--site", current_site.domain)
    old_prefix = old_key.partition(".")[0]

    new_key = run("renew", "--name", "svc-bot")

    assert new_key != old_key
    bot = User.objects.get(username="svc-bot")
    assert bot.api_keys.count() == 2
    assert bot.api_keys.get(prefix=old_prefix).revoked
    assert bot.api_keys.filter(revoked=False).count() == 1
    assert ServiceAPIKey.objects.get_from_key(new_key).site == current_site
    with pytest.raises(ServiceAPIKey.DoesNotExist):
        ServiceAPIKey.objects.get_from_key(old_key)


@pytest.mark.django_db
def test_renew_twice_keeps_a_single_usable_key(current_site):
    run("create", "--name", "svc-bot", "--site", current_site.domain)
    run("renew", "--name", "svc-bot")

    last_key = run("renew", "--name", "svc-bot")

    bot = User.objects.get(username="svc-bot")
    assert bot.api_keys.count() == 3
    assert bot.api_keys.filter(revoked=False).count() == 1
    assert ServiceAPIKey.objects.get_from_key(last_key).site == current_site


@pytest.mark.django_db
def test_each_key_gets_a_unique_name(current_site):
    run("create", "--name", "svc-bot", "--site", current_site.domain)
    run("renew", "--name", "svc-bot")

    names = list(ServiceAPIKey.objects.values_list("name", flat=True))

    assert len(set(names)) == 2
    assert all(name.startswith("svc-bot-") for name in names)


@pytest.mark.django_db
def test_key_name_fits_even_with_a_long_username(current_site):
    username = "b" * 150
    run("create", "--name", username, "--site", current_site.domain)

    name = ServiceAPIKey.objects.get().name
    assert len(name) <= ServiceAPIKey._meta.get_field("name").max_length
    assert name.startswith("b")


@pytest.mark.django_db
def test_disable_deactivates_bot_and_revokes_keys(current_site):
    key = run("create", "--name", "svc-bot", "--site", current_site.domain)

    run("disable", "--name", "svc-bot")

    bot = User.objects.get(username="svc-bot")
    assert not bot.is_active
    assert bot.profile.disabled is not None
    assert bot.api_keys.count() == 1
    assert not bot.api_keys.filter(revoked=False).exists()
    with pytest.raises(ServiceAPIKey.DoesNotExist):
        ServiceAPIKey.objects.get_from_key(key)


@pytest.mark.django_db
def test_disable_refuses_an_already_disabled_bot(current_site):
    run("create", "--name", "svc-bot", "--site", current_site.domain)
    run("disable", "--name", "svc-bot")
    disabled = User.objects.get(username="svc-bot").profile.disabled

    with pytest.raises(CommandError, match="already disabled"):
        run("disable", "--name", "svc-bot")

    bot = User.objects.get(username="svc-bot")
    assert bot.profile.disabled == disabled


@pytest.mark.django_db
def test_renew_without_a_key_says_so(service_account):
    with pytest.raises(CommandError, match="no API key to renew"):
        run("renew", "--name", service_account.username)


@pytest.mark.django_db
def test_enable_without_a_key_leaves_the_bot_disabled(service_account):
    deactivate_user(service_account)

    with pytest.raises(CommandError, match="no API key to enable it with"):
        run("enable", "--name", service_account.username)

    service_account.refresh_from_db()
    assert not service_account.is_active
    assert service_account.profile.disabled is not None


@pytest.mark.django_db
def test_renew_refuses_a_disabled_bot(current_site):
    run("create", "--name", "svc-bot", "--site", current_site.domain)
    run("disable", "--name", "svc-bot")

    with pytest.raises(CommandError):
        run("renew", "--name", "svc-bot")

    assert not ServiceAPIKey.objects.filter(revoked=False).exists()


@pytest.mark.django_db
def test_enable_reactivates_bot_with_a_single_new_key(current_site):
    old_key = run("create", "--name", "svc-bot", "--site", current_site.domain)
    run("disable", "--name", "svc-bot")
    # a key left usable by hand must not survive the enable
    ServiceAPIKey.objects.update(revoked=False)

    new_key = run("enable", "--name", "svc-bot")

    bot = User.objects.get(username="svc-bot")
    assert bot.is_active
    assert bot.profile.disabled is None
    assert bot.api_keys.count() == 2
    assert bot.api_keys.filter(revoked=False).count() == 1
    assert ServiceAPIKey.objects.get_from_key(new_key).site == current_site
    with pytest.raises(ServiceAPIKey.DoesNotExist):
        ServiceAPIKey.objects.get_from_key(old_key)


@pytest.mark.django_db
def test_enable_refuses_an_active_bot(current_site):
    key = run("create", "--name", "svc-bot", "--site", current_site.domain)

    with pytest.raises(CommandError):
        run("enable", "--name", "svc-bot")

    assert ServiceAPIKey.objects.count() == 1
    assert ServiceAPIKey.objects.get_from_key(key)


@pytest.mark.django_db
@pytest.mark.parametrize("action", ["renew", "disable", "enable"])
def test_renew_disable_and_enable_never_touch_human_users(action):
    human = baker.make(User, username="human", is_active=action != "enable")

    with pytest.raises(CommandError):
        run(action, "--name", "human")

    human.refresh_from_db()
    assert human.is_active == (action != "enable")
