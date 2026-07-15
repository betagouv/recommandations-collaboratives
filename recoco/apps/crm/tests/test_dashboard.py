import re
from datetime import timedelta

import pytest
from actstream import action
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from model_bakery.recipe import Recipe, foreign_key
from notifications.signals import notify
from pytest_django.asserts import assertContains, assertNotContains

from recoco import verbs
from recoco.apps.geomatics import models as geomatics_models
from recoco.apps.projects import models as projects_models
from recoco.apps.projects.utils import assign_advisor
from recoco.apps.tasks import models as tasks_models
from recoco.utils import login


@pytest.mark.django_db
def test_low_reach_not_available_for_non_staff_users(client):
    url = reverse("crm-list-projects-low-reach")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_low_reach_available_for_staff_users(current_site, client, make_project):
    url = reverse("crm-list-projects-low-reach")

    make_project(current_site)
    make_project(current_site)

    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_low_reach_as_csv_not_available_for_non_staff_users(client):
    url = reverse("crm-projects-low-reach-csv")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_low_reach_as_csv_available_for_staff_users(current_site, client, make_project):
    url = reverse("crm-projects-low-reach-csv")

    make_project(current_site)
    make_project(current_site)

    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_site_dashboard_shows_project_actions_to_staff(current_site, client):
    project = baker.make(projects_models.Project, sites=[current_site])
    action.send(project, verb="Was here", target=project)

    other_site = baker.make(site_models.Site)
    with settings.SITE_ID.override(other_site.pk):
        other = baker.make(projects_models.Project, sites=[other_site])
        action.send(other, verb="Was not here", target=other)

    url = reverse("crm-site-dashboard")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200

    assertContains(response, "Was here")
    assertNotContains(response, "Was not here")


@pytest.mark.django_db
def test_site_dashboard_shows_advisor_request_actions_to_staff(current_site, client):
    project = baker.make(projects_models.Project, sites=[current_site])
    action.send(project, verb=verbs.User.ADVISOR_REQUEST, target=project)

    url = reverse("crm-site-dashboard")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, verbs.User.ADVISOR_REQUEST)


@pytest.mark.django_db
def test_site_dashboard_hides_other_site_project_notifications(request, client):
    user = baker.make(auth_models.User)

    other_site = baker.make(site_models.Site)
    with settings.SITE_ID.override(other_site.pk):
        other_project = baker.make(projects_models.Project, sites=[other_site])
        # a notification for this project
        verb = verbs.CRM.NOTE_CREATED
        notify.send(
            sender=user,
            recipient=user,
            verb=verb,
            action_object=other_project,
            target=other_project,
            public=False,  # only appear on crm stream
        )

    url = reverse("crm-site-dashboard")
    with login(client, user=user, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200

    assertNotContains(response, verb)


########################################################################
# low reach query parameters parsing
########################################################################


@pytest.mark.django_db
def test_low_reach_defaults_to_all_and_15_days(client):
    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200
    assert response.context["days"] == 15
    assert response.context["status_filter"] == "all"
    assert response.context["mine_only"] is False
    assert response.context["search_q"] == ""


@pytest.mark.django_db
def test_low_reach_accepts_known_days_filter(client):
    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"days": 90})

    assert response.status_code == 200
    assert response.context["days"] == 90


@pytest.mark.django_db
def test_low_reach_falls_back_on_invalid_days(client):
    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"days": "not-an-int"})

    assert response.status_code == 200
    assert response.context["days"] == 15


@pytest.mark.django_db
def test_low_reach_falls_back_on_unknown_status(client):
    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"status": "something-else"})

    assert response.status_code == 200
    assert response.context["status_filter"] == "all"


@pytest.mark.django_db
def test_low_reach_search_query_is_stripped(client):
    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"q": "  hello  "})

    assert response.status_code == 200
    assert response.context["search_q"] == "hello"


########################################################################
# low reach query filtering rules
########################################################################


@pytest.fixture
def public_task_recipe(project_recipe, current_site):
    """Attach a public task in PROPOSED status to a project."""
    yield Recipe(
        tasks_models.Task,
        site=current_site,
        project=foreign_key(project_recipe),
        public=True,
        status=tasks_models.Task.PROPOSED,
    )


@pytest.fixture
def project_old_recipe(project_recipe):
    """Push a project's last members activity 30 days in the past."""
    old = project_recipe.extend(
        last_members_activity_at=timezone.now() - timedelta(days=30)
    )
    yield old


@pytest.mark.django_db
def test_low_reach_lists_project_with_public_task_and_no_engagement(
    current_site, client, project_old_recipe, public_task_recipe
):
    project = project_old_recipe.make()
    public_task_recipe.make(project=project)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, project.name)


@pytest.mark.django_db
def test_low_reach_hides_project_with_task_in_progress(
    current_site, client, make_project, project_old_recipe, public_task_recipe
):
    project = project_old_recipe.make()
    public_task_recipe.make(project=project)
    public_task_recipe.make(project=project, status=tasks_models.Task.INPROGRESS)
    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        # Engagement-based exclusion now only applies to the "no_reaction" filter.
        response = client.get(url, data={"status": "no_reaction"})

    assert response.status_code == 200
    assertNotContains(response, project.name)


@pytest.mark.django_db
def test_low_reach_hides_project_without_public_task(
    current_site, client, project_old_recipe
):
    empty_project = project_old_recipe.make()

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200
    assertNotContains(response, empty_project.name)


@pytest.mark.django_db
def test_low_reach_low_read_filter_keeps_barely_read_only(
    current_site, client, project_old_recipe, public_task_recipe
):
    not_read_project = project_old_recipe.make()
    public_task_recipe.make(project=not_read_project)

    well_read = project_old_recipe.make()
    public_task_recipe.make(project=well_read, visited=True)
    public_task_recipe.make(project=well_read, visited=True)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"status": "low_read"})

    assert response.status_code == 200
    assertContains(response, not_read_project.name)
    assertNotContains(response, well_read.name)


@pytest.mark.django_db
def test_low_reach_mine_only_filters_by_switchtender(
    current_site, client, project_old_recipe, public_task_recipe
):
    mine = project_old_recipe.make()
    public_task_recipe.make(project=mine)

    other = project_old_recipe.make()
    public_task_recipe.make(project=other)

    advisor = baker.make(auth_models.User)
    advisor.profile.sites.add(current_site)
    assign_advisor(advisor, mine, current_site)

    url = reverse("crm-list-projects-low-reach")
    with login(client, user=advisor, groups=["example_com_staff"]):
        response = client.get(url, data={"mine": "1"})

    assert response.status_code == 200
    assertContains(response, mine.name)
    assertNotContains(response, other.name)


@pytest.mark.django_db
def test_low_reach_search_matches_project_name(
    current_site, client, project_old_recipe, public_task_recipe
):
    target = project_old_recipe.make(name="UniqueLighthouse")
    public_task_recipe.make(project=target)

    other = project_old_recipe.make()
    public_task_recipe.make(project=other)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"q": "Lighthouse"})

    assert response.status_code == 200
    assertContains(response, target.name)
    assertNotContains(response, other.name)


@pytest.mark.django_db
def test_low_reach_days_zero_disables_time_filter(
    current_site, client, project_recipe, public_task_recipe
):
    recent = project_recipe.make()
    public_task_recipe.make(project=recent)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"days": 0})

    assert response.status_code == 200
    assertContains(response, recent.name)


########################################################################
# CSV export columns & filename
########################################################################


@pytest.mark.django_db
def test_low_reach_csv_uses_french_headers_and_filename(
    current_site, client, project_old_recipe, public_task_recipe
):
    commune = baker.make(geomatics_models.Commune, name="Ville", insee="12345")

    project = project_old_recipe.make(commune=commune)
    public_task_recipe.make(project=project)

    url = reverse("crm-projects-low-reach-csv")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200

    body = response.content.decode("utf-8")
    first_line = body.splitlines()[0]
    assert first_line == (
        '"nom_dossier","commune","insee","conseillers","recos_lues","recos_total",'
        '"derniere_activite","derniere_reco","statut","referent_prenom","referent_nom",'
        '"referent_organisation","referent_telephone","referent_email","referent_fonction"'
    )

    assert re.fullmatch(
        r'attachment; filename="projets-a-relancer-\d{4}-\d{2}-\d{2}-\d{6}\.csv"',
        response["Content-Disposition"],
    )


# eof
