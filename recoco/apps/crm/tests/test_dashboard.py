from datetime import timedelta

import pytest
from actstream import action
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from notifications.signals import notify
from pytest_django.asserts import assertContains, assertNotContains

from recoco import verbs
from recoco.apps.geomatics import models as geomatics_models
from recoco.apps.home import models as home_models
from recoco.apps.projects import models as projects_models
from recoco.apps.tasks import models as tasks_models
from recoco.utils import login


@pytest.mark.django_db
def test_low_reach_not_available_for_non_staff_users(client):
    url = reverse("crm-list-projects-low-reach")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_low_reach_available_for_staff_users(request, client, make_project):
    url = reverse("crm-list-projects-low-reach")

    current_site = get_current_site(request)

    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

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
def test_low_reach_as_csv_available_for_staff_users(request, client, make_project):
    url = reverse("crm-projects-low-reach-csv")

    current_site = get_current_site(request)

    make_project(current_site)
    make_project(current_site)

    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_site_dashboard_shows_project_actions_to_staff(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site])
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
def test_site_dashboard_shows_advisor_request_actions_to_staff(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site])
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
def test_low_reach_defaults_to_no_reaction_and_15_days(request, client):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200
    assert response.context["days"] == 15
    assert response.context["status_filter"] == "no_reaction"
    assert response.context["mine_only"] is False
    assert response.context["search_q"] == ""


@pytest.mark.django_db
def test_low_reach_accepts_known_days_filter(request, client):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"days": 90})

    assert response.status_code == 200
    assert response.context["days"] == 90


@pytest.mark.django_db
def test_low_reach_falls_back_on_invalid_days(request, client):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"days": "not-an-int"})

    assert response.status_code == 200
    assert response.context["days"] == 15


@pytest.mark.django_db
def test_low_reach_falls_back_on_unknown_status(request, client):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"status": "something-else"})

    assert response.status_code == 200
    assert response.context["status_filter"] == "no_reaction"


@pytest.mark.django_db
def test_low_reach_search_query_is_stripped(request, client):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"q": "  hello  "})

    assert response.status_code == 200
    assert response.context["search_q"] == "hello"


########################################################################
# low reach query filtering rules
########################################################################


def _add_public_task(project, site, **kwargs):
    """Attach a public task in PROPOSED status to a project."""
    return baker.make(
        tasks_models.Task,
        project=project,
        site=site,
        public=True,
        status=tasks_models.Task.PROPOSED,
        **kwargs,
    )


def _make_old(project):
    """Push a project's last members activity 30 days in the past."""
    project.last_members_activity_at = timezone.now() - timedelta(days=30)
    project.save()


@pytest.mark.django_db
def test_low_reach_lists_project_with_public_task_and_no_engagement(
    request, client, make_project
):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    project = make_project(site, name="VisibleProject")
    _make_old(project)
    _add_public_task(project, site)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, "VisibleProject")


@pytest.mark.django_db
def test_low_reach_hides_project_with_task_in_progress(request, client, make_project):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    project = make_project(site, name="EngagedProject")
    _make_old(project)
    _add_public_task(project, site)
    baker.make(
        tasks_models.Task,
        project=project,
        site=site,
        public=True,
        status=tasks_models.Task.INPROGRESS,
    )

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200
    assertNotContains(response, "EngagedProject")


@pytest.mark.django_db
def test_low_reach_hides_project_without_public_task(request, client, make_project):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    project = make_project(site, name="EmptyProject")
    _make_old(project)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200
    assertNotContains(response, "EmptyProject")


@pytest.mark.django_db
def test_low_reach_low_read_filter_keeps_barely_read_only(
    request, client, make_project
):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    not_read = make_project(site, name="NotReadProject")
    _make_old(not_read)
    _add_public_task(not_read, site)

    well_read = make_project(site, name="WellReadProject")
    _make_old(well_read)
    _add_public_task(well_read, site, visited=True)
    _add_public_task(well_read, site, visited=True)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"status": "low_read"})

    assert response.status_code == 200
    assertContains(response, "NotReadProject")
    assertNotContains(response, "WellReadProject")


@pytest.mark.django_db
def test_low_reach_mine_only_filters_by_switchtender(request, client, make_project):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    mine = make_project(site, name="MineProject")
    _make_old(mine)
    _add_public_task(mine, site)

    other = make_project(site, name="OtherProject")
    _make_old(other)
    _add_public_task(other, site)

    advisor = baker.make(auth_models.User)
    advisor.profile.sites.add(site)
    baker.make(
        projects_models.ProjectSwitchtender,
        site=site,
        switchtender=advisor,
        project=mine,
    )

    url = reverse("crm-list-projects-low-reach")
    with login(client, user=advisor, groups=["example_com_staff"]):
        response = client.get(url, data={"mine": "1"})

    assert response.status_code == 200
    assertContains(response, "MineProject")
    assertNotContains(response, "OtherProject")


@pytest.mark.django_db
def test_low_reach_search_matches_project_name(request, client, make_project):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    target = make_project(site, name="UniqueLighthouse")
    _make_old(target)
    _add_public_task(target, site)

    other = make_project(site, name="OtherProject")
    _make_old(other)
    _add_public_task(other, site)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"q": "Lighthouse"})

    assert response.status_code == 200
    assertContains(response, "UniqueLighthouse")
    assertNotContains(response, "OtherProject")


@pytest.mark.django_db
def test_low_reach_days_zero_disables_time_filter(request, client, make_project):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    recent = make_project(site, name="RecentProject")
    _add_public_task(recent, site)

    url = reverse("crm-list-projects-low-reach")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, data={"days": 0})

    assert response.status_code == 200
    assertContains(response, "RecentProject")


########################################################################
# CSV export columns & filename
########################################################################


@pytest.mark.django_db
def test_low_reach_csv_uses_french_headers_and_filename(request, client, make_project):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)
    commune = baker.make(geomatics_models.Commune, name="Ville", insee="12345")

    project = make_project(site, commune=commune)
    _make_old(project)
    _add_public_task(project, site)

    url = reverse("crm-projects-low-reach-csv")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200

    body = response.content.decode("utf-8")
    first_line = body.splitlines()[0]
    expected_headers = [
        "nom_dossier",
        "commune",
        "insee",
        "conseillers",
        "recos_lues",
        "recos_total",
        "derniere_activite",
        "derniere_reco",
        "statut",
        "referent_prenom",
        "referent_nom",
        "referent_organisation",
        "referent_telephone",
        "referent_email",
        "referent_fonction",
    ]
    for header in expected_headers:
        assert header in first_line

    assert "projets-a-relancer-" in response["Content-Disposition"]


# eof
