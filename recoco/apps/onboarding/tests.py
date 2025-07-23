import pytest
from django.contrib.auth import models as auth
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe

from recoco.apps.geomatics import models as geomatics
from recoco.apps.home import models as home_models
from recoco.apps.invites import models as invites_models
from recoco.apps.onboarding import models as onboarding_models
from recoco.apps.projects import models as projects_models
from recoco.apps.survey import models as survey_models
from recoco.utils import login


########################################################################
# Onboarding page for user
########################################################################
@pytest.mark.django_db
def test_onboarding_page_with_logged_in_user_is_reachable(request, client):
    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
    )

    with login(client):
        url = reverse("onboarding-project")
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
def test_onboarding_with_existing_account_redirects_to_signin(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    data = {
        "email": "a@exAmpLe.Com",
        "name": "a project",
        "location": "some place",
        "postcode": "62170",
        "insee": "62044",
        "description": "a description",
    }

    baker.make(auth.User, email=data["email"].lower(), username=data["email"])

    response = client.post(reverse("onboarding-project"), data=data, follow=True)
    last_url, status_code = response.redirect_chain[-1]
    assert status_code == 302
    assert last_url.startswith(reverse("onboarding-signin"))


@pytest.mark.django_db
def test_onboarding_with_account_on_other_site_redirects_to_signin(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    other_site = baker.make(Site)

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    data = {
        "email": "a@exAmpLe.Com",
        "name": "a project",
        "location": "some place",
        "postcode": "62170",
        "insee": "62044",
        "description": "a description",
    }

    user = baker.make(auth.User, email=data["email"].lower(), username=data["email"])
    user.profile.sites.add(other_site)

    response = client.post(reverse("onboarding-project"), data=data, follow=True)
    last_url, status_code = response.redirect_chain[-1]
    assert status_code == 302
    assert last_url.startswith(reverse("onboarding-signin"))


@pytest.mark.django_db
def test_onboarding_with_nonexisting_account_redirects_to_signup(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    data = {
        "email": "a@eXampLe.com",
        "name": "a project",
        "location": "some place",
        "postcode": "62170",
        "insee": "62044",
        "description": "a description",
    }
    response = client.post(reverse("onboarding-project"), data=data, follow=True)
    last_url, status_code = response.redirect_chain[-1]
    assert status_code == 302
    assert last_url == reverse("onboarding-signup")


@pytest.mark.django_db
def test_onboarding_signup_redirects_to_project_form_when_logged(request, client):
    current_site = get_current_site(request)

    baker.make(
        home_models.SiteConfiguration,
        site=current_site,
    )

    with login(client):
        response = client.post(reverse("onboarding-signup"), follow=True)
        last_url, status_code = response.redirect_chain[-1]
        assert status_code == 302
        assert last_url == reverse("onboarding-project")


@pytest.mark.django_db
def test_performing_onboarding_signup_create_a_new_user_and_logs_in(request, client):
    current_site = get_current_site(request)

    baker.make(
        home_models.SiteConfiguration,
        site=current_site,
    )

    data = {
        "email": "a@example.com",
        "phone": "0610101010",
        "role": "Ouistiti",
        "password": "blah",
        "first_name": "john",
        "last_name": "doe",
        "org_name": "MyOrg",
    }

    response = client.post(reverse("onboarding-signup"), data=data)

    assert response.status_code == 302

    # the user and profile are filled according to provided information
    user = auth.User.objects.get(username=data["email"])
    assert user.email == data["email"]
    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]
    assert current_site in user.profile.sites.all()
    assert user.profile.organization.name == data["org_name"]
    assert user.profile.organization_position == data["role"]
    assert user.profile.phone_no == data["phone"]

    # present if logged_in
    assert int(client.session["_auth_user_id"]) == user.pk


@pytest.mark.django_db
def test_performing_onboarding_signup_with_existing_user_redirects_to_signin(
    request, client
):
    current_site = get_current_site(request)

    baker.make(
        home_models.SiteConfiguration,
        site=current_site,
    )

    user = baker.make(auth.User, username="bob@bob.fr")

    user_count = auth.User.objects.count()

    data = {
        "email": user.username,
        "phone": "0610101010",
        "role": "Ouistiti",
        "password": "blah",
        "first_name": "john",
        "last_name": "doe",
        "org_name": "MyOrg",
    }

    response = client.post(reverse("onboarding-signup"), data=data, follow=True)
    last_url, status_code = response.redirect_chain[-1]
    assert status_code == 302
    assert last_url.startswith(reverse("onboarding-signin"))

    assert auth.User.objects.count() == user_count

    user.refresh_from_db()

    assert user.profile.organization_position != data["role"]
    assert user.first_name != data["first_name"]
    assert user.last_name != data["last_name"]
    assert user.email != data["email"]
    assert not user.profile.organization
    assert user.profile.phone_no != data["phone"]

    # present if logged_in
    assert not client.session.get("_auth_user_id", None)


#########################################
# Onboarding: Step2, project info
#########################################


@pytest.mark.django_db
def test_performing_onboarding_creates_a_new_project(request, client):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    data = {
        "name": "a project",
        "location": "some place",
        "postcode": "62170",
        "insee": "62044",
        "description": "a description",
    }

    with login(client):
        response = client.post(reverse("onboarding-project"), data=data)
        assert response.status_code == 302

    project = projects_models.Project.on_site.first()
    assert project
    assert project.name == data["name"]
    assert project.project_sites.current().status == "DRAFT"
    assert project.project_sites.current().is_origin is True
    assert len(project.ro_key) == 32


@pytest.mark.django_db
def test_performing_onboarding_with_survey_fills_it(request, client):
    site = get_current_site(request)

    survey = baker.make(survey_models.Survey)

    survey_simple_question = baker.make(
        survey_models.Question, question_set__survey=survey
    )
    survey_qcm_question = baker.make(
        survey_models.Question, question_set__survey=survey
    )
    baker.make(
        survey_models.Choice, question=survey_qcm_question, text="no", value="no"
    )

    baker.make(
        home_models.SiteConfiguration,
        site=site,
        onboarding_questions=[survey_simple_question, survey_qcm_question],
        project_survey=survey,
    )

    data = {
        "name": "a project",
        "location": "some place",
        "postcode": "62170",
        "insee": "62044",
        "description": "a description",
        f"q{survey_simple_question.id}-comment": "blah",
        f"q{survey_qcm_question.id}-answer": "no",
    }

    with login(client):
        response = client.post(reverse("onboarding-project"), data=data)
        assert response.status_code == 302

    project = projects_models.Project.on_site.first()
    assert project

    session = project.survey_session
    assert session


@pytest.mark.django_db
def test_performing_onboarding_sends_notification_to_project_moderators(
    request, client
):
    current_site = get_current_site(request)

    baker.make(
        home_models.SiteConfiguration,
        site=current_site,
    )

    staff_group = auth.Group.objects.get(name="example_com_staff")
    moderator = Recipe(
        auth.User,
        email="moderator@example.com",
        groups=[staff_group],
    ).make()

    project_data = {
        "name": "a project",
        "location": "some place",
        "postcode": "62170",
        "insee": "62044",
        "description": "blah",
    }

    with login(client):
        response = client.post(
            reverse("onboarding-project"), data=project_data, follow=True
        )
        last_url, status_code = response.redirect_chain[-1]
        assert status_code == 302

        project = projects_models.Project.objects.last()
        assert last_url == reverse("onboarding-summary", args=[project.pk])

    assert moderator.notifications.count() == 1


@pytest.mark.django_db
def test_performing_onboarding_discard_unknown_postal_code(request, client):
    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

    data = {
        "name": "a project",
        "location": "some place",
        "postcode": "62170",
        "insee": "62044",
        "description": "a description",
    }

    with login(client):
        response = client.post(reverse("onboarding-project"), data=data)
        assert response.status_code == 302

    project = projects_models.Project.on_site.all()[0]
    assert project.commune is None


#################################################################
# onboarding by an advisor for someone else
#################################################################


# -- set user
@pytest.mark.django_db
def test_create_prefilled_project_set_user_is_not_reachable_without_login(
    request, client
):
    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
    )

    url = reverse("onboarding-prefill-set-user")
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_prefilled_project_set_user_is_not_reachable_with_simple_login(
    request, client
):
    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
    )

    with login(client):
        response = client.get(reverse("onboarding-prefill-set-user"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_prefilled_project_set_user_reachable_by_switchtenders(request, client):
    site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration,
        site=site,
    )

    with login(client, groups=["example_com_advisor"]):
        response = client.get(reverse("onboarding-prefill-set-user"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_create_prefilled_project_set_user_memorized_in_session(request, client):
    site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration,
        site=site,
    )

    data = {
        "email": "my@email.com",
        "first_name": "Camille",
        "last_name": "Dupont",
        "phone": "066666666",
        "org_name": "ACME",
        "role": "Ouistiti",
    }

    with login(client, groups=["example_com_advisor"]):
        response = client.post(reverse("onboarding-prefill-set-user"), data)

    assert response.status_code == 302

    assert client.session.get("prefill_set_user", None) is not None


# -- project
@pytest.mark.django_db
def test_create_prefilled_project_is_not_reachable_without_login(request, client):
    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
    )

    url = reverse("onboarding-prefill")
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_prefilled_project_is_not_reachable_with_simple_login(request, client):
    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
    )

    with login(client):
        response = client.get(reverse("onboarding-prefill"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_prefilled_project_reachable_by_switchtenders(request, client):
    site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration,
        site=site,
    )

    data = {
        "email": "my@email.com",
        "first_name": "Camille",
        "last_name": "Dupont",
        "phone": "066666666",
        "org_name": "ACME",
        "role": "Ouistiti",
    }

    with login(client, groups=["example_com_advisor"]):
        response = client.post(reverse("onboarding-prefill-set-user"), data)
        response = client.get(reverse("onboarding-prefill"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_create_prefilled_project_without_user_set_redirects(request, client):
    site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration,
        site=site,
    )

    with login(client, groups=["example_com_advisor"]):
        response = client.get(reverse("onboarding-prefill"), follow=True)
        last_url, status_code = response.redirect_chain[-1]

    assert status_code == 302
    assert last_url == reverse("onboarding-prefill-set-user")


@pytest.mark.django_db
def test_create_prefilled_project_creates_a_new_project(request, client):
    site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration,
        site=site,
    )

    baker.make(geomatics.Commune, insee="62044", postal="62170")

    user_data = {
        "email": "my@email.com",
        "first_name": "Camille",
        "last_name": "Dupont",
        "phone": "066666666",
        "org_name": "ACME",
        "role": "Ouistiti",
    }

    project_data = {
        "name": "a project",
        "location": "some place",
        "postcode": "62170",
        "insee": "62044",
        "description": "blah",
    }

    with login(client, groups=["example_com_advisor"]) as submitter:
        response = client.post(reverse("onboarding-prefill-set-user"), data=user_data)
        assert response.status_code == 302
        response = client.post(
            reverse("onboarding-prefill"), data=project_data, follow=True
        )
        last_url, status_code = response.redirect_chain[-1]
        assert status_code == 302

    # Project
    project = projects_models.Project.on_site.all()[0]

    assert last_url == reverse("projects-project-detail-overview", args=[project.pk])

    assert project.name == project_data["name"]
    assert project.location == project_data["location"]
    assert project.commune is not None
    assert project.description == project_data["description"]

    assert project.project_sites.current().status == "TO_PROCESS"
    assert project.project_sites.current().is_origin is True

    assert len(project.ro_key) == 32

    # User
    user = auth.User.objects.get(username=user_data["email"])
    owner = project.owner

    assert owner == user

    assert user_data["email"].lower() == owner.email
    assert user_data["email"].lower() == owner.username
    assert user_data["first_name"] == owner.first_name
    assert user_data["last_name"] == owner.last_name
    assert site in owner.profile.sites.all()

    assert submitter in project.switchtenders.all()

    assert submitter == project.submitted_by

    invite = invites_models.Invite.objects.first()
    assert invite.project == project


@pytest.mark.django_db
def test_prefill_project_with_survey_fills_it(request, client):
    site = get_current_site(request)

    survey = baker.make(survey_models.Survey)

    survey_simple_question = baker.make(
        survey_models.Question, question_set__survey=survey
    )
    survey_qcm_question = baker.make(
        survey_models.Question, question_set__survey=survey
    )
    baker.make(
        survey_models.Choice, question=survey_qcm_question, text="no", value="no"
    )

    baker.make(
        home_models.SiteConfiguration,
        site=site,
        onboarding_questions=[survey_simple_question, survey_qcm_question],
        project_survey=survey,
    )
    user_data = {
        "email": "my@email.com",
        "first_name": "Camille",
        "last_name": "Dupont",
        "phone": "066666666",
        "org_name": "ACME",
        "role": "Ouistiti",
    }

    data = {
        "name": "a project",
        "location": "some place",
        "postcode": "62170",
        "insee": "62044",
        "description": "a description",
        f"q{survey_simple_question.id}-comment": "blah",
        f"q{survey_qcm_question.id}-answer": "no",
    }

    with login(client, groups=["example_com_advisor"]):
        response = client.post(reverse("onboarding-prefill-set-user"), data=user_data)
        assert response.status_code == 302
        response = client.post(reverse("onboarding-project"), data=data)
        assert response.status_code == 302

    project = projects_models.Project.on_site.first()
    assert project

    session = project.survey_session
    assert session


########################################################################
# Selecting proper commune insee code for multiple commune postal code
########################################################################


@pytest.mark.django_db
def test_selecting_proper_commune_completes_project_creation(
    request, client, make_project
):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    selected = Recipe(geomatics.Commune, postal="12345").make()
    membership = baker.make(
        projects_models.ProjectMember, member__is_staff=False, is_owner=True
    )
    project = make_project(
        site=get_current_site(request),
        projectmember_set=[membership],
        commune=commune,
    )

    with login(client, user=membership.member):
        response = client.post(
            reverse("onboarding-select-commune", args=[project.id]),
            data={"commune": selected.id},
        )
    project = projects_models.Project.on_site.get(id=project.id)
    assert project.commune == selected
    assert response.status_code == 302
    expected = reverse("survey-project-session", args=[project.id]) + "?first_time=1"
    assert response.url == expected


@pytest.mark.django_db
def test_proper_commune_selection_contains_all_possible_commmunes(request, client):
    expected = [
        Recipe(geomatics.Commune, postal="12345").make(),
        Recipe(geomatics.Commune, postal="12345").make(),
    ]
    unexpected = Recipe(geomatics.Commune, postal="67890").make()

    membership = baker.make(
        projects_models.ProjectMember, member__is_staff=False, is_owner=True
    )
    project = Recipe(
        projects_models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        commune=expected[1],
    ).make()

    with login(client, user=membership.member):
        response = client.get(
            reverse("onboarding-select-commune", args=[project.id]),
        )
    page = str(response.content)
    for commune in expected:
        assert commune.name in page
    assert unexpected.name not in page


# eof
