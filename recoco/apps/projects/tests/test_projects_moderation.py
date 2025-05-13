from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import models as auth
from django.urls import reverse
from guardian.shortcuts import get_user_perms
from model_bakery import baker
from model_bakery.recipe import Recipe

from recoco.apps.geomatics import models as geomatics
from recoco.apps.geomatics.models import Commune, Department
from recoco.apps.home.models import AdvisorAccessRequest, SiteConfiguration
from recoco.apps.projects.models import Project, ProjectMember
from recoco.utils import login


@pytest.mark.django_db
def test_project_moderation_not_available_for_non_moderators(
    current_site, client, project_draft
):
    baker.make(SiteConfiguration, site=current_site)
    project = Recipe(Project, sites=[current_site]).make()

    with login(client):
        for url in [
            reverse("projects-moderation-list"),
            reverse("projects-moderation-project-refuse", args=[project.id]),
            reverse("projects-moderation-project-accept", args=[project.id]),
        ]:
            response = client.get(url)
            assert response.status_code == 403


@pytest.mark.django_db
def test_project_moderation_accept_and_redirect(current_site, client, project_draft):
    baker.make(SiteConfiguration, site=current_site)
    owner = Recipe(auth.User, username="owner@owner.co").make()

    baker.make(ProjectMember, project=project_draft, member=owner, is_owner=True)

    updated_on_before = project_draft.updated_on
    url = reverse("projects-moderation-project-accept", args=[project_draft.id])

    with login(client, groups=["example_com_staff"]) as moderator:
        moderator.profile.sites.add(current_site)
        response = client.post(url)

    project = Project.on_site.get(id=project_draft.id)
    assert project.project_sites.current().status == "TO_PROCESS"
    assert project.updated_on > updated_on_before

    # check updated permissions
    assert "invite_collaborators" in get_user_perms(owner, project)

    assert response.status_code == 302


@pytest.mark.django_db
def test_project_moderation_accept_without_owner_and_redirect(
    current_site, client, project_draft
):
    baker.make(SiteConfiguration, site=current_site)

    updated_on_before = project_draft.updated_on
    url = reverse("projects-moderation-project-accept", args=[project_draft.id])

    with login(client, groups=["example_com_staff"]) as moderator:
        moderator.profile.sites.add(current_site)
        response = client.post(url)

    project = Project.on_site.get(id=project_draft.id)
    assert project.project_sites.current().status == "TO_PROCESS"
    assert project.updated_on > updated_on_before

    assert response.status_code == 302


@pytest.mark.django_db
def test_project_moderation_notifies_regional_actors_when_accepted(
    current_site, client, make_project
):
    baker.make(SiteConfiguration, site=current_site)

    st_group = auth.Group.objects.get(name="example_com_advisor")

    dpt_nord = Recipe(geomatics.Department, code=59, name="Nord").make()
    commune = Recipe(
        geomatics.Commune, name="Lille", postal="59000", department=dpt_nord
    ).make()

    regional_actor = Recipe(auth.User).make()
    regional_actor.groups.add(st_group)
    regional_actor.profile.departments.add(dpt_nord)
    regional_actor.profile.sites.add(current_site)

    membership = baker.make(ProjectMember, member=regional_actor, is_owner=True)

    project = make_project(
        site=current_site,
        status="DRAFT",
        commune=commune,
        projectmember_set=[membership],
    )

    with login(client, groups=["example_com_advisor", "example_com_staff"]) as user:
        user.profile.sites.add(current_site)
        response = client.post(
            reverse("projects-moderation-project-accept", args=[project.id])
        )
        assert response.status_code == 302

    assert regional_actor.notifications.count() == 1


@pytest.mark.django_db
def test_project_moderation_does_not_notify_non_regional_actors_on_accept(
    current_site, client
):
    baker.make(SiteConfiguration, site=current_site)
    group = auth.Group.objects.get(name="example_com_advisor")

    dpt_nord = Recipe(geomatics.Department, code=59, name="Nord").make()
    dpt_pdc = Recipe(geomatics.Department, code=62, name="Pas de Calais").make()
    commune = Recipe(
        geomatics.Commune, name="Lille", postal="59000", department=dpt_nord
    ).make()

    non_regional_actor = baker.make(auth.User, email="somewhere@else.info")
    non_regional_actor.groups.add(group)
    non_regional_actor.profile.departments.add(dpt_pdc)

    nr_membership = baker.make(
        ProjectMember,
        member=non_regional_actor,
    )

    owner_membership = baker.make(ProjectMember, is_owner=True)
    project = Recipe(
        Project,
        sites=[current_site],
        commune=commune,
        projectmember_set=[owner_membership],
    ).make()

    with login(client, user=nr_membership.member, groups=["example_com_advisor"]):
        client.post(reverse("projects-moderation-project-accept", args=[project.id]))

    assert non_regional_actor.notifications.count() == 0


@pytest.mark.django_db
def test_project_moderation_refuse_and_redirect(current_site, client):
    baker.make(SiteConfiguration, site=current_site)
    owner = Recipe(auth.User, username="owner@owner.co").make()
    project = Recipe(Project, sites=[current_site]).make()
    baker.make(ProjectMember, project=project, member=owner, is_owner=True)

    updated_on_before = project.updated_on
    url = reverse("projects-moderation-project-refuse", args=[project.id])

    with login(client, groups=["example_com_staff"]) as moderator:
        moderator.profile.sites.add(current_site)
        response = client.post(url)

    project = Project.on_site.get(id=project.id)
    assert project.status == "REJECTED"
    assert project.updated_on > updated_on_before

    assert response.status_code == 302


@pytest.mark.multisite
@pytest.mark.django_db
def test_project_moderation_accept_on_secondary_site(
    current_site, client, project_draft
):
    baker.make(SiteConfiguration, site=current_site)
    owner = Recipe(auth.User, username="owner@owner.co").make()

    baker.make(ProjectMember, project=project_draft, member=owner, is_owner=True)

    updated_on_before = project_draft.updated_on
    url = reverse("projects-moderation-project-accept", args=[project_draft.id])

    with login(client, groups=["example_com_staff"]) as moderator:
        moderator.profile.sites.add(current_site)
        response = client.post(url)

    project = Project.on_site.get(id=project_draft.id)
    assert project.project_sites.current().status == "TO_PROCESS"
    assert project.updated_on > updated_on_before

    # check updated permissions
    assert "invite_collaborators" in get_user_perms(owner, project)

    assert response.status_code == 302


class TestProjectModerationAdvisorRefuse:
    @pytest.mark.django_db
    def test_redirect_anonymous(self, client):
        response = client.get(reverse("projects-moderation-advisor-refuse", args=[1]))
        assert response.status_code == 302
        assert (
            response.url
            == "/accounts/login/?next=/projects/moderation/advisor/1/refuse/"
        )

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=True))
    def test_not_found(self, client):
        user = baker.make(auth.User)
        client.force_login(user)
        response = client.post(
            reverse("projects-moderation-advisor-refuse", args=[999])
        )
        assert response.status_code == 404

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=False))
    def test_not_moderator(self, client):
        user = baker.make(auth.User)
        client.force_login(user)
        response = client.post(
            reverse("projects-moderation-advisor-refuse", args=[999])
        )
        assert response.status_code == 403

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=True))
    def test_get_not_allowed(self, client):
        user = baker.make(auth.User)
        client.force_login(user)
        response = client.get(reverse("projects-moderation-advisor-refuse", args=[999]))
        assert response.status_code == 405

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=True))
    def test_post_request(self, client, current_site):
        moderator = baker.make(auth.User)
        client.force_login(moderator)

        user = baker.make(auth.User)
        dpt = baker.make(Department, code="64", name="Pyrénées-Atlantiques")
        project = baker.make(
            Project,
            sites=[current_site],
            commune=baker.make(Commune, name="Bayonne", postal="64100", department=dpt),
        )

        advisor_access_request = baker.make(
            AdvisorAccessRequest, site=current_site, user=user, status="PENDING"
        )
        advisor_access_request.departments.add(dpt)

        with patch(
            "recoco.apps.projects.views.unassign_advisor"
        ) as mock_unassign_advisor:
            response = client.post(
                reverse(
                    "projects-moderation-advisor-refuse",
                    args=[advisor_access_request.pk],
                )
            )

        assert response.status_code == 302
        assert response.url == "/projects/moderation/"
        mock_unassign_advisor.assert_called_once_with(
            user=user, project=project, site=current_site
        )

        advisor_access_request.refresh_from_db()
        assert advisor_access_request.status == "REJECTED"


class TestProjectModerationAdvisorAccept:
    @pytest.mark.django_db
    def test_redirect_anonymous(self, client):
        response = client.get(reverse("projects-moderation-advisor-accept", args=[1]))
        assert response.status_code == 302
        assert (
            response.url
            == "/accounts/login/?next=/projects/moderation/advisor/1/accept/"
        )

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=True))
    def test_not_found(self, client):
        user = baker.make(auth.User)
        client.force_login(user)
        response = client.post(
            reverse("projects-moderation-advisor-accept", args=[999])
        )
        assert response.status_code == 404

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=False))
    def test_not_moderator(self, client):
        user = baker.make(auth.User)
        client.force_login(user)
        response = client.post(
            reverse("projects-moderation-advisor-accept", args=[999])
        )
        assert response.status_code == 403

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=True))
    def test_get_not_allowed(self, client):
        user = baker.make(auth.User)
        client.force_login(user)
        response = client.get(reverse("projects-moderation-advisor-accept", args=[999]))
        assert response.status_code == 405

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=True))
    def test_post_request(self, client, current_site):
        moderator = baker.make(auth.User)
        client.force_login(moderator)

        user = baker.make(auth.User)
        dpt = baker.make(Department, code="64", name="Pyrénées-Atlantiques")
        project = baker.make(
            Project,
            sites=[current_site],
            commune=baker.make(Commune, name="Bayonne", postal="64100", department=dpt),
        )

        advisor_access_request = baker.make(
            AdvisorAccessRequest, site=current_site, user=user, status="PENDING"
        )
        advisor_access_request.departments.add(dpt)

        with patch(
            "recoco.apps.projects.views.assign_advisor"
        ) as mock_unassign_advisor:
            response = client.post(
                reverse(
                    "projects-moderation-advisor-accept",
                    args=[advisor_access_request.pk],
                )
            )

        assert response.status_code == 302
        assert response.url == "/projects/moderation/"
        mock_unassign_advisor.assert_called_once_with(
            user=user, project=project, site=current_site
        )

        advisor_access_request.refresh_from_db()
        assert advisor_access_request.status == "ACCEPTED"


class TestProjectModerationAdvisorModify:
    @pytest.mark.django_db
    def test_redirect_anonymous(self, client):
        response = client.get(reverse("projects-moderation-advisor-modify", args=[1]))
        assert response.status_code == 302
        assert (
            response.url
            == "/accounts/login/?next=/projects/moderation/advisor/1/modify/"
        )

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=True))
    def test_not_found(self, client):
        user = baker.make(auth.User)
        client.force_login(user)
        response = client.post(
            reverse("projects-moderation-advisor-modify", args=[999])
        )
        assert response.status_code == 404

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=False))
    def test_not_moderator(self, client):
        user = baker.make(auth.User)
        client.force_login(user)
        response = client.post(
            reverse("projects-moderation-advisor-modify", args=[999])
        )
        assert response.status_code == 403

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=True))
    def test_get_not_allowed(self, client):
        user = baker.make(auth.User)
        client.force_login(user)
        response = client.get(reverse("projects-moderation-advisor-modify", args=[999]))
        assert response.status_code == 405

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=True))
    def test_post_request(self, client, current_site):
        moderator = baker.make(auth.User)
        client.force_login(moderator)

        user = baker.make(auth.User)
        dpt = baker.make(Department, code="64", name="Pyrénées-Atlantiques")
        project = baker.make(
            Project,
            sites=[current_site],
            commune=baker.make(Commune, name="Bayonne", postal="64100", department=dpt),
        )

        advisor_access_request = baker.make(
            AdvisorAccessRequest, site=current_site, user=user, status="ACCEPTED"
        )
        advisor_access_request.departments.add(dpt)

        with patch(
            "recoco.apps.projects.views.unassign_advisor"
        ) as mock_unassign_advisor:
            response = client.post(
                reverse(
                    "projects-moderation-advisor-modify",
                    args=[advisor_access_request.pk],
                )
            )

        assert response.status_code == 302
        assert response.url == f"/advisor-access-request/{advisor_access_request.pk}/"
        mock_unassign_advisor.assert_called_once_with(
            user=user, project=project, site=current_site
        )

        advisor_access_request.refresh_from_db()
        assert advisor_access_request.status == "PENDING"
