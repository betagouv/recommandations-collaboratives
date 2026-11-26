import pytest
from allauth.account.models import Login
from allauth.account.stages import LoginStageController
from allauth.mfa.models import Authenticator
from allauth.socialaccount.models import SocialAccount, SocialLogin
from django.contrib.auth import models as auth_models
from django.test import RequestFactory
from django.urls import reverse
from model_bakery import baker

from recoco.apps.home.adapters import UVAccountAdapter
from recoco.apps.home.stages import RecocoMFAAuthenticateStage
from recoco.utils import confirm_mail


@pytest.fixture
def user_with_mfa(db):
    user = baker.make(auth_models.User, email="mfa@example.com")
    Authenticator.objects.create(
        user=user, type=Authenticator.Type.TOTP, data={"secret": "x"}
    )
    return user


def _stage(user, provider=None):
    signal_kwargs = None
    if provider:
        sociallogin = SocialLogin(
            user=user, account=SocialAccount(user=user, provider=provider)
        )
        signal_kwargs = {"sociallogin": sociallogin}
    login = Login(user=user, signal_kwargs=signal_kwargs)
    request = RequestFactory().get("/")
    request.session = {}
    controller = LoginStageController(request, login)
    return RecocoMFAAuthenticateStage(controller, request, login)


def test_login_stages_use_recoco_mfa_stage():
    stages = UVAccountAdapter().get_login_stages()
    assert "recoco.apps.home.stages.RecocoMFAAuthenticateStage" in stages
    assert "allauth.mfa.stages.AuthenticateStage" not in stages


@pytest.mark.django_db
def test_mfa_required_without_social_login(user_with_mfa):
    stage = _stage(user_with_mfa)
    assert stage._should_handle(stage.request)


@pytest.mark.django_db
def test_mfa_skipped_for_proconnect_login(user_with_mfa):
    stage = _stage(user_with_mfa, provider="proconnect")
    assert not stage._should_handle(stage.request)


@pytest.mark.django_db
def test_mfa_required_for_other_social_provider(user_with_mfa):
    stage = _stage(user_with_mfa, provider="other")
    assert stage._should_handle(stage.request) is True


@pytest.mark.django_db
def test_password_login_with_mfa_redirects_to_mfa(client, user_with_mfa):
    confirm_mail(user_with_mfa)
    password = "mon mot de passe"  # nosec B105
    user_with_mfa.set_password(password)
    user_with_mfa.save()

    response = client.post(
        reverse("account_login"),
        data={"login": user_with_mfa.email, "password": password},
    )

    assert response.status_code == 302
    assert response.url == reverse("mfa_authenticate")
