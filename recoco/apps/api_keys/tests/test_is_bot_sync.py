import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import modelform_factory
from model_bakery import baker

from ..models import ServiceAPIKey


def set_bot(user, value):
    user.profile.is_bot = value
    user.profile.save()


@pytest.mark.django_db
def test_cannot_create_key_for_non_bot_user(current_site):
    user = baker.make(User, is_active=True)

    with pytest.raises(ValidationError):
        ServiceAPIKey.objects.create_key(name="svc", user=user, site=current_site)

    assert not ServiceAPIKey.objects.exists()


@pytest.mark.django_db
def test_can_create_key_for_bot_user(current_site):
    user = baker.make(User, is_active=True)
    set_bot(user, True)

    ServiceAPIKey.objects.create_key(name="svc", user=user, site=current_site)

    assert ServiceAPIKey.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_admin_choices_only_offer_bot_users(current_site):
    bot = baker.make(User, is_active=True)
    set_bot(bot, True)
    human = baker.make(User, is_active=True)

    form = modelform_factory(ServiceAPIKey, fields=["user"])()
    choices = form.fields["user"].queryset

    assert bot in choices
    assert human not in choices


@pytest.mark.django_db
def test_unsetting_is_bot_deletes_keys(current_site):
    bot = baker.make(User, is_active=True)
    set_bot(bot, True)
    other_bot = baker.make(User, is_active=True)
    set_bot(other_bot, True)
    ServiceAPIKey.objects.create_key(name="a", user=bot, site=current_site)
    ServiceAPIKey.objects.create_key(name="b", user=bot, site=current_site)
    ServiceAPIKey.objects.create_key(name="c", user=other_bot, site=current_site)

    set_bot(bot, False)

    assert not ServiceAPIKey.objects.filter(user=bot).exists()
    assert ServiceAPIKey.objects.filter(user=other_bot).count() == 1


@pytest.mark.django_db
def test_saving_bot_profile_keeps_keys(current_site):
    bot = baker.make(User, is_active=True)
    set_bot(bot, True)
    ServiceAPIKey.objects.create_key(name="a", user=bot, site=current_site)

    bot.profile.organization_position = "robot"
    bot.profile.save()

    assert ServiceAPIKey.objects.filter(user=bot).count() == 1
