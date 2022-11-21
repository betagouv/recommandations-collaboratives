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
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import login


# Baker addons
def gen_onboarding_func():
    return """[{ "type": "text",
    "required": false,
    "label": "Text Field",
    "className": "form-control",
    "name": "text-1657009260220-0",
    "subtype": "text" }]"""


baker.generators.add("dynamic_forms.models.FormField", gen_onboarding_func)


########################################################################
# Onboarding page
########################################################################


def test_onboarding_page_is_reachable_without_login(request, client):
    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

    url = reverse("projects-onboarding")
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-projects-onboarding"')


@pytest.mark.django_db
def test_performing_onboarding_create_a_new_project(request, client):
    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

    data = {
        "name": "a project",
        "email": "a@example.com",
        "location": "some place",
        "org_name": "MyOrg",
        "first_name": "john",
        "last_name": "doe",
        "description": "a description",
        "impediment_kinds": ["Autre"],
        "response_0": "blah",
        "impediments": "some impediment",
    }
    response = client.post(reverse("projects-onboarding"), data=data)

    project = projects_models.Project.on_site.first()
    assert project
    assert project.name == "a project"
    assert project.status == "DRAFT"
    assert len(project.ro_key) == 32
    assert data["email"] == project.members.first().username
    assert data["email"] == project.members.first().email
    note = projects_models.Note.objects.all()[0]
    assert note.project == project
    assert note.public
    assert note.content == f"# Demande initiale\n\n{project.description}\n\n\n"
    assert response.status_code == 302
    assert response["Location"].startswith(reverse("home-user-setup-password"))


@pytest.mark.django_db
def test_performing_onboarding_create_a_new_user_and_logs_in(request, client):
    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

    data = {
        "name": "a project",
        "email": "a@example.com",
        "description": "my desc",
        "postal_code": "59800",
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

    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]

    assert int(client.session["_auth_user_id"]) == user.pk


@pytest.mark.django_db
def test_performing_onboarding_stores_initial_info(request, client):
    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

    data = {
        "name": "a project",
        "email": "a@example.com",
        "description": "my desc",
        "postal_code": "59800",
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

    note = projects_models.Note.objects.first()
    assert data["description"] in note.content
    assert note.public is True


@pytest.mark.django_db
def test_performing_onboarding_does_not_allow_account_stealing(request, client):
    user = baker.make(auth.User, username="existing@example.com")

    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

    data = {
        "name": "a project",
        "email": user.username,
        "description": "my desc",
        "postal_code": "59800",
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
    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

    md_group = Recipe(auth.Group, name="project_moderator").make()
    st_group, created = auth.Group.objects.get_or_create(name="switchtender")
    moderator = Recipe(
        auth.User, email="moderator@example.com", groups=[md_group, st_group]
    ).make()

    data = {
        "name": "a project",
        "email": "a@example.com",
        "location": "some place",
        "org_name": "MyOrg",
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
    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

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
def test_performing_onboarding_discard_unknown_postal_code(request, client):
    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

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
                "response_0": "blah",
                "postcode": "12345",
                "impediment_kinds": ["Autre"],
                "impediments": "some impediment",
            },
        )

    assert response.status_code == 302
    project = projects_models.Project.on_site.all()[0]
    assert project.commune is None


@pytest.mark.django_db
def test_performing_onboarding_allow_select_on_multiple_communes(request, client):
    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

    commune = baker.make(geomatics.Commune, postal="12345")
    baker.make(geomatics.Commune, postal="12345")
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
                "response_0": "blah",
                "postcode": commune.postal,
                "impediment_kinds": ["Autre"],
                "impediments": "some impediment",
            },
        )

    assert response.status_code == 302
    project = projects_models.Project.on_site.first()
    url = reverse("projects-onboarding-select-commune", args=[project.id])
    assert response.url == (url)


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
