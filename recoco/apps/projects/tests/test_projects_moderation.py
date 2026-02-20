from unittest.mock import ANY, Mock, patch

import pytest
from django.contrib.auth import models as auth
from django.urls import reverse
from guardian.shortcuts import get_user_perms
from model_bakery import baker
from model_bakery.recipe import Recipe

from recoco.apps.geomatics import models as geomatics
from recoco.apps.geomatics.models import Department
from recoco.apps.home.models import AdvisorAccessRequest, SiteConfiguration
from recoco.apps.projects.models import Project, ProjectMember
from recoco.utils import get_group_for_site, login


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

    owner = Recipe(
        auth.User,
        username="owner@owner.co",
        email="owner@owner.co",
        first_name="Anakin",
        last_name="Skywalker",
    ).make()

    project = Recipe(Project, sites=[current_site], name="My project").make()
    baker.make(ProjectMember, project=project, member=owner, is_owner=True)

    updated_on_before = project.updated_on
    url = reverse("projects-moderation-project-refuse", args=[project.id])

    with (
        login(client, groups=["example_com_staff"]) as moderator,
        patch("recoco.apps.projects.views.send_email") as mock_send_email,
        patch(
            "recoco.apps.communication.digests.make_project_digest",
            Mock(return_value="mocked_project_digest"),
        ) as mock_make_project_digest,
    ):
        moderator.profile.sites.add(current_site)
        response = client.post(url)

    project = Project.on_site.get(id=project.id)
    assert project.status == "REJECTED"
    assert project.updated_on > updated_on_before

    assert response.status_code == 302
    assert project.action_object_actions.count() == 1

    mock_make_project_digest.assert_called_once_with(
        project=project,
        user=owner,
    )

    mock_send_email.assert_called_once_with(
        template_name="project_refused",
        recipients=[
            {
                "name": "Anakin Skywalker",
                "email": "owner@owner.co",
            }
        ],
        params={
            "project": "mocked_project_digest",
        },
    )


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
        baker.make(SiteConfiguration, site=current_site)

        moderator = baker.make(auth.User)
        client.force_login(moderator)

        dept_64 = baker.make(Department, code="64", name="Pyrénées-Atlantiques")
        dept_33 = baker.make(Department, code="33", name="Gironde")

        user = baker.make(auth.User, first_name="Anakin", last_name="Skywalker")
        user.profile.departments.add(dept_33)

        advisor_access_request = baker.make(
            AdvisorAccessRequest,
            site=current_site,
            user=user,
            status="PENDING",
            comment="My comment",
        )
        advisor_access_request.departments.add(dept_64)

        with patch("recoco.apps.projects.views.send_email") as mock_send_email:
            response = client.post(
                reverse(
                    "projects-moderation-advisor-refuse",
                    args=[advisor_access_request.pk],
                )
            )

        assert response.status_code == 302
        assert response.url == "/projects/moderation/"

        advisor_access_request.refresh_from_db()
        assert advisor_access_request.status == "REJECTED"

        user.refresh_from_db()
        assert list(user.profile.departments.values_list("code", flat=True)) == ["33"]

        advisor_group = get_group_for_site("advisor", current_site)
        assert not user.groups.filter(name=advisor_group.name).exists()

        mock_send_email.assert_called_once_with(
            template_name="advisor_access_request_refused",
            recipients=[
                {
                    "name": "Anakin Skywalker",
                    "email": user.email,
                }
            ],
            params={
                "message": "My comment",
            },
        )


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

        dept_64 = baker.make(Department, code="64", name="Pyrénées-Atlantiques")
        dept_33 = baker.make(Department, code="33", name="Gironde")

        user = baker.make(auth.User, first_name="Anakin", last_name="Skywalker")
        user.profile.departments.add(dept_33)

        advisor_access_request = baker.make(
            AdvisorAccessRequest,
            site=current_site,
            user=user,
            status="PENDING",
            comment="My comment",
        )
        advisor_access_request.departments.add(dept_64)

        with patch("recoco.apps.projects.views.send_email") as mock_send_email:
            response = client.post(
                reverse(
                    "projects-moderation-advisor-accept",
                    args=[advisor_access_request.pk],
                )
            )

        assert response.status_code == 302
        assert response.url == "/projects/moderation/"

        user.refresh_from_db()
        assert list(user.profile.departments.values_list("code", flat=True)) == [
            "33",
            "64",
        ]

        advisor_group = get_group_for_site("advisor", current_site)
        assert user.groups.filter(name=advisor_group.name).exists()

        mock_send_email.assert_called_once_with(
            template_name="advisor_access_request_accepted",
            recipients=[
                {
                    "name": "Anakin Skywalker",
                    "email": user.email,
                }
            ],
            params={
                "message": "My comment",
                "dashboard_url": ANY,
            },
        )
        assert (
            mock_send_email.mock_calls[0]
            .kwargs["params"]["dashboard_url"]
            .startswith("https://example.com/projects/?sesame=")
        )


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

        dept_64 = baker.make(Department, code="64", name="Pyrénées-Atlantiques")
        dept_33 = baker.make(Department, code="33", name="Gironde")

        user = baker.make(auth.User)
        user.profile.departments.add(dept_33, dept_64)

        advisor_access_request = baker.make(
            AdvisorAccessRequest, site=current_site, user=user, status="ACCEPTED"
        )
        advisor_access_request.departments.add(dept_64)

        response = client.post(
            reverse(
                "projects-moderation-advisor-modify",
                args=[advisor_access_request.pk],
            )
        )

        assert response.status_code == 302
        assert response.url == f"/advisor-access-request/{advisor_access_request.pk}/"

        advisor_access_request.refresh_from_db()
        assert advisor_access_request.status == "PENDING"

        user.refresh_from_db()
        assert list(user.profile.departments.values_list("code", flat=True)) == [
            "33",
            "64",
        ]

        advisor_group = get_group_for_site("advisor", current_site)
        assert not user.groups.filter(name=advisor_group.name).exists()
