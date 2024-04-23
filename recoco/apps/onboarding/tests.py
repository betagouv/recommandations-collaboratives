import pytest
from django.contrib.auth import models as auth
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe
from recoco.apps.geomatics import models as geomatics
from recoco.apps.home import models as home_models
from recoco.apps.onboarding import models as onboarding_models
from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.projects import models as projects_models
from recoco.apps.invites import models as invites_models
from recoco.utils import login


########################################################################
# Onboarding page for user
########################################################################
@pytest.mark.django_db
def test_onboarding_page_without_login_redirects_to_signin(request, client):
    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
    )

    url = reverse("onboarding")
    response = client.get(url, follow=True)
    last_url, status_code = response.redirect_chain[-1]
    assert status_code == 302
    assert last_url == reverse("account_login")


@pytest.mark.django_db
def test_onboarding_page_with_logged_in_user_redirects_to_step2(request, client):
    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
    )

    with login(client):
        url = reverse("onboarding")
        response = client.get(url, follow=True)
        last_url, status_code = response.redirect_chain[-1]
        assert status_code == 302
        assert last_url == reverse("onboarding-project")


#########################################
# Onboarding: Step1, user signnup
#########################################


@pytest.mark.django_db
def test_onboarding_signup_with_nonexisting_account(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    data = {
        "email": "a@eXampLe.com",
    }
    response = client.post(reverse("onboarding"), data=data, follow=True)
    last_url, status_code = response.redirect_chain[-1]
    assert status_code == 302
    assert last_url == reverse("onboarding-signup")


@pytest.mark.django_db
def test_onboarding_signup_with_existing_account(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    data = {
        "email": "a@exAmpLe.Com",
    }

    baker.make(auth.User, email=data["email"].lower(), username=data["email"])

    response = client.post(reverse("onboarding"), data=data, follow=True)
    last_url, status_code = response.redirect_chain[-1]
    assert status_code == 302
    assert last_url.startswith(reverse("account_login"))


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


#########################################
# Onboarding: Step2, project info
#########################################


@pytest.mark.django_db
def test_performing_onboarding_create_a_new_project(request, client):
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
    assert project.status == "DRAFT"
    assert len(project.ro_key) == 32


@pytest.mark.django_db
def test_performing_onboarding_creates_initial_info_note(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    data = {
        "name": "a project",
        "description": "my desc",
        "postal_code": "62170",
        "insee": "62040",
        "location": "some place",
    }
    response = client.post(reverse("onboarding"), data=data)

    assert response.status_code == 302

    project = projects_models.Project.on_site.first()
    assert project

    note = projects_models.Note.objects.first()
    assert data["description"] in note.content
    assert note.public is True


@pytest.mark.django_db
def test_performing_onboarding_signup_does_not_allow_account_stealing(request, client):
    user = baker.make(auth.User, username="existing@example.com")

    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    data = {
        "name": "a project",
        "email": user.username,
        "description": "my desc",
        "postal_code": "59800",
        "phone": "0610101010",
        "location": "some place",
        "first_name": "john",
        "last_name": "doe",
        "org_name": "MyOrg",
        "response_0": "blah",
        "impediment_kinds": ["Autre"],
        "impediments": "some impediment",
    }

    response = client.post(reverse("onboarding"), data=data)

    assert response.status_code == 302
    assert client.session.get("_auth_user_id", None) is None
    assert projects_models.Project.on_site.count() == 0


@pytest.mark.django_db
def test_performing_onboarding_sends_notification_to_project_moderators(
    request, client
):
    current_site = get_current_site(request)
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=current_site,
        onboarding=onboarding,
    )

    staff_group = auth.Group.objects.get(name="example_com_staff")
    # st_group = auth.Group.objects.get(name="example_com_advisor")
    moderator = Recipe(
        auth.User,
        email="moderator@example.com",
        groups=[staff_group],
    ).make()

    data = {
        "name": "a project",
        "email": "a@example.com",
        "location": "some place",
        "org_name": "MyOrg",
        "phone": "0610101010",
        "description": "my desc",
        "first_name": "john",
        "last_name": "doe",
        "response_0": "blah",
        "impediment_kinds": ["Autre"],
        "impediments": "some impediment",
    }

    client.post(reverse("onboarding"), data=data)

    assert moderator.notifications.count() == 1


@pytest.mark.django_db
def test_performing_onboarding_sets_existing_postal_code(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    commune = Recipe(geomatics.Commune, postal="12345").make()
    with login(client):
        response = client.post(
            reverse("onboarding"),
            data={
                "name": "a project",
                "email": "a@example.com",
                "location": "some place",
                "org_name": "My Org",
                "description": "my desc",
                "phone": "0610101010",
                "first_name": "john",
                "last_name": "doe",
                "postcode": commune.postal,
                "response_0": "blah",
                "impediment_kinds": ["Autre"],
                "impediments": "some impediment",
            },
        )

    assert response.status_code == 302
    project = projects_models.Project.on_site.all()[0]
    assert project.commune == commune


@pytest.mark.django_db
def test_performing_onboarding_assigns_current_site_to_organization(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    commune = Recipe(geomatics.Commune, postal="12345").make()

    data = {
        "name": "a project",
        "email": "a@example.com",
        "location": "some place",
        "org_name": "My Org",
        "description": "my desc",
        "first_name": "john",
        "last_name": "doe",
        "phone": "9338383838",
        "postcode": commune.postal,
        "response_0": "blah",
        "impediment_kinds": ["Autre"],
        "impediments": "some impediment",
    }

    with login(client):
        response = client.post(
            reverse("onboarding"),
            data=data,
        )

    assert response.status_code == 302
    org = addressbook_models.Organization.on_site.first()
    assert org.name == data["org_name"]


@pytest.mark.django_db
def test_performing_onboarding_discard_unknown_postal_code(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    with login(client):
        response = client.post(
            reverse("onboarding"),
            data={
                "name": "a project",
                "email": "a@example.com",
                "location": "some place",
                "org_name": "My Org",
                "description": "my desc",
                "first_name": "john",
                "last_name": "doe",
                "phone": "0610101010",
                "response_0": "blah",
                "postcode": "12345",
                "impediment_kinds": ["Autre"],
                "impediments": "some impediment",
            },
        )

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
        response = client.get(reverse("onboarding-set-user"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_prefilled_project_set_user_reachable_by_switchtenders(request, client):
    site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration,
        site=site,
    )

    with login(client, groups=["example_com_advisor"]):
        response = client.get(reverse("onboarding-prefill"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_create_prefilled_project_set_user_creates_new_account(request, client):
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
        "organization": "ACME",
        "role": "Ouistiti",
    }

    with login(client, groups=["example_com_advisor"]):
        response = client.post(reverse("onboarding-prefill-set-user"), data)

    assert response.status_code == 302

    user = auth.User.objects.get(username=data["email"])
    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]
    assert user.email == data["email"]
    assert user.profile.phone == data["phone"]
    assert user.profile.organization == data["ACME"]
    assert user.profile.organization_position == data["role"]

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
        "first_name": "Camille",
        "last_name": "Dupont",
        "phone": "066666666",
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
    onboarding = onboarding_models.Onboarding.objects.first()
    site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration,
        site=site,
        onboarding=onboarding,
    )

    data = {
        "name": "a project",
        "email": "a@ExAmple.Com",
        "location": "some place",
        "phone": "03939382828",
        "postcode": "59000",
        "org_name": "my org",
        "description": "blah",
        "first_name": "john",
        "last_name": "doe",
        "response_0": "blah",
    }
    with login(client, groups=["example_com_advisor"]) as user:
        response = client.post(reverse("onboarding-prefill"), data=data)

    project = projects_models.Project.on_site.all()[0]
    assert project.name == data["name"]
    assert project.status == "TO_PROCESS"
    assert len(project.ro_key) == 32

    owner = project.owner

    assert data["email"].lower() == owner.email
    assert data["first_name"] == owner.first_name
    assert data["last_name"] == owner.last_name
    assert site in owner.profile.sites.all()

    assert user in project.switchtenders.all()

    assert user == project.submitted_by

    invite = invites_models.Invite.objects.first()
    assert invite.project == project

    assert response.status_code == 302


@pytest.mark.django_db
def test_created_prefilled_project_stores_initial_info(request, client):
    site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration,
        site=site,
    )

    data = {
        "name": "a project",
        "email": "a@example.com",
        "description": "my desc",
        "postal_code": "59800",
        "location": "some place",
        "first_name": "john",
        "phone": "0610101010",
        "last_name": "doe",
        "org_name": "MyOrg",
    }

    with login(client, groups=["example_com_advisor"]):
        response = client.post(reverse("onboarding-prefill"), data=data)

    assert response.status_code == 302

    project = projects_models.Project.on_site.first()
    assert project

    note = projects_models.Note.objects.first()
    assert data["description"] in note.content
    assert note.public is True


########################################################################
# Selecting proper commune insee code for multiple commune postal code
########################################################################


@pytest.mark.django_db
def test_selecting_proper_commune_completes_project_creation(request, client):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    selected = Recipe(geomatics.Commune, postal="12345").make()
    membership = baker.make(
        projects_models.ProjectMember, member__is_staff=False, is_owner=True
    )
    project = Recipe(
        projects_models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        commune=commune,
    ).make()

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
