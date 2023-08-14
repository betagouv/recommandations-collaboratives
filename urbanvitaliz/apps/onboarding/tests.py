import pytest
from django.contrib.auth import models as auth
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlencode
from model_bakery import baker
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.home import models as home_models
from urbanvitaliz.apps.onboarding import models as onboarding_models
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.apps.invites import models as invites_models
from urbanvitaliz.utils import login


########################################################################
# Baker addons for using dynamic forms in onboarding
########################################################################


def gen_onboarding_func():
    return """[{ "type": "text",
    "required": false,
    "label": "Text Field",
    "className": "form-control",
    "name": "text-1657009260220-0",
    "subtype": "text" }]"""


baker.generators.add("dynamic_forms.models.FormField", gen_onboarding_func)


########################################################################
# Onboarding page for user
########################################################################


@pytest.mark.django_db
def test_onboarding_page_is_reachable_without_login(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    url = reverse("projects-onboarding")
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-projects-onboarding"')


@pytest.mark.django_db
def test_performing_onboarding_create_a_new_project(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    data = {
        "name": "a project",
        "email": "a@exAmpLe.Com",
        "location": "some place",
        "phone": "0610101010",
        "org_name": "MyOrg",
        "first_name": "john",
        "last_name": "doe",
        "description": "a description",
        "impediment_kinds": ["Autre"],
        "response_0": "blah",
        "impediments": "some impediment",
    }
    response = client.post(reverse("projects-onboarding"), data=data)
    assert response.status_code == 302

    project = projects_models.Project.on_site.first()
    assert project
    assert project.name == "a project"
    assert project.status == "DRAFT"
    assert len(project.ro_key) == 32
    note = projects_models.Note.objects.all()[0]
    assert note.project == project
    assert note.public
    assert note.content == f"# Demande initiale\n\n{project.description}\n\n\n"
    assert response.status_code == 302
    assert response["Location"].startswith(reverse("home-user-setup-password"))


@pytest.mark.django_db
def test_performing_onboarding_create_a_new_user_and_logs_in(request, client):
    current_site = get_current_site(request)
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=current_site,
        onboarding=onboarding,
    )

    data = {
        "name": "a project",
        "email": "a@example.com",
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
    response = client.post(reverse("projects-onboarding"), data=data)

    assert response.status_code == 302

    project = projects_models.Project.on_site.first()
    assert project
    user = project.members.first()

    assert project.owner == user
    assert project.submitted_by == user

    next_url = urlencode(
        {"next": reverse("survey-project-session", args=[project.id]) + "?first_time=1"}
    )
    url = reverse("home-user-setup-password")
    assert response.url == (f"{url}?{next_url}")

    # the user and profile are filled according to provided information
    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]
    assert current_site in user.profile.sites.all()
    assert user.profile.organization.name == data["org_name"]
    assert user.profile.phone_no == data["phone"]

    assert int(client.session["_auth_user_id"]) == user.pk


@pytest.mark.django_db
def test_onboarding_fills_existing_user_and_profile_missing_info(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    data = {
        "name": "a project",
        "email": "a@exAmpLe.Com",
        "location": "some place",
        "org_name": "MyOrg",
        "phone": "+3893889393399",
        "first_name": "john",
        "last_name": "doe",
        "description": "a description",
        "impediment_kinds": ["Autre"],
        "response_0": "blah",
        "impediments": "some impediment",
    }

    email = data["email"].lower()
    with login(client, username=email) as user:
        response = client.post(reverse("projects-onboarding"), data=data)

    project = projects_models.Project.objects.first()

    assert response.status_code == 302
    assert response["Location"].startswith(
        reverse("survey-project-session", args=[project.id])
    )

    user.refresh_from_db()

    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]
    assert user.profile.organization.name == data["org_name"]
    assert user.profile.phone_no == data["phone"]


@pytest.mark.django_db
def test_onbording_do_not_replace_existing_user_email_when_logged_in(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    data = {
        "name": "a project",
        "email": "a@exAmpLe.Com",
        "location": "some place",
        "org_name": "MyOrg",
        "phone": "+3893889393399",
        "first_name": "john",
        "last_name": "doe",
        "description": "a description",
        "impediment_kinds": ["Autre"],
        "response_0": "blah",
        "impediments": "some impediment",
    }

    user_email = "user@existing.mail"
    with login(client, username=user_email, email=user_email) as user:
        response = client.post(reverse("projects-onboarding"), data=data)

    project = projects_models.Project.objects.first()

    assert response.status_code == 302
    assert response["Location"].startswith(
        reverse("survey-project-session", args=[project.id])
    )

    user.refresh_from_db()  # fonctionne dans ce contexte

    assert user.email == user_email


@pytest.mark.django_db
def test_onboarding_known_not_logged_user_login_and_preserve_data(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    data = {
        "name": "a new project for existing user",
        "email": "a@exAmpLe.Com",
        "location": "some place",
        "org_name": "My organization",
        "phone": "+3893889393399",
        "first_name": "john",
        "last_name": "doe",
        "description": "a description of my new project",
        "response_0": "blah",
    }

    # someone exists with this email (which is lower case)
    email = data["email"].lower()
    baker.make(auth.User, email=email, username=email)

    # i am not connected
    response = client.post(reverse("projects-onboarding"), data=data)

    # send me to login to prove i am the one
    assert response.status_code == 302
    assert response["Location"].startswith(reverse("account_login"))

    assert client.session["onboarding_existing_data"] == {
        "first_name": "john",
        "last_name": "doe",
        "phone": "+3893889393399",
        "org_name": "My organization",
        "email": "a@example.com",
        "name": "a new project for existing user",
        "location": "some place",
        "insee": "",
        "description": "a description of my new project",
        "response": {"Vide": "blah"},
        "postcode": "",
    }


@pytest.mark.django_db
def test_onboarding_reuse_session_content_when_logged_user_is_back(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    data = {
        "first_name": "john",
        "last_name": "doe",
        "phone": "+3893889393399",
        "org_name": "My organization",
        "email": "a@example.com",
        "name": "a new project for existing user",
        "location": "some place",
        "insee": "",
        "description": "a description of my new project",
        "response": {"Vide": "blah"},
        "postcode": "",
    }

    with login(client, username=data["email"], email=data["email"]):
        session = client.session
        session["onboarding_existing_data"] = data
        session.save()

        response = client.get(reverse("projects-onboarding"))

    assert response.status_code == 200
    # data is there when i am back to onboarding
    assertContains(response, data["name"])
    assertContains(response, data["description"])
    assertContains(response, data["location"])


@pytest.mark.django_db
def test_performing_onboarding_stores_initial_info(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    data = {
        "name": "a project",
        "email": "a@example.com",
        "description": "my desc",
        "postal_code": "59800",
        "location": "some place",
        "first_name": "john",
        "last_name": "doe",
        "phone": "0610101010",
        "org_name": "MyOrg",
        "response_0": "blah",
        "impediment_kinds": ["Autre"],
        "impediments": "some impediment",
    }
    response = client.post(reverse("projects-onboarding"), data=data)

    assert response.status_code == 302

    project = projects_models.Project.on_site.first()
    assert project

    note = projects_models.Note.objects.first()
    assert data["description"] in note.content
    assert note.public is True


@pytest.mark.django_db
def test_performing_onboarding_does_not_allow_account_stealing(request, client):
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

    response = client.post(reverse("projects-onboarding"), data=data)

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

    client.post(reverse("projects-onboarding"), data=data)

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
            reverse("projects-onboarding"),
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
            reverse("projects-onboarding"),
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
            reverse("projects-onboarding"),
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


@pytest.mark.django_db
def test_create_prefilled_project_is_not_reachable_without_login(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    url = reverse("projects-project-prefill")
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_prefilled_project_is_not_reachable_with_simple_login(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    with login(client):
        response = client.get(reverse("projects-project-prefill"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_prefilled_project_reachable_by_switchtenders(request, client):
    onboarding = onboarding_models.Onboarding.objects.first()
    site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration,
        site=site,
        onboarding=onboarding,
    )

    with login(client, groups=["example_com_advisor"]):
        response = client.get(reverse("projects-project-prefill"))

    assert response.status_code == 200


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
        response = client.post(reverse("projects-project-prefill"), data=data)

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
    onboarding = onboarding_models.Onboarding.objects.first()
    site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration,
        site=site,
        onboarding=onboarding,
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
        "response_0": "blah",
        "impediment_kinds": ["Autre"],
        "impediments": "some impediment",
    }

    with login(client, groups=["example_com_advisor"]):
        response = client.post(reverse("projects-project-prefill"), data=data)

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
            reverse("projects-onboarding-select-commune", args=[project.id]),
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
            reverse("projects-onboarding-select-commune", args=[project.id]),
        )
    page = str(response.content)
    for commune in expected:
        assert commune.name in page
    assert unexpected.name not in page


# eof
