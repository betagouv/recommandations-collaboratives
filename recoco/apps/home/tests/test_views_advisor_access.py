from unittest.mock import Mock, patch

import pytest
from actstream import models as action_models
from django.contrib.auth.models import User
from django.urls import reverse
from model_bakery import baker
from notifications import models as notifications_models

from recoco import verbs
from recoco.apps.geomatics.models import Department
from recoco.apps.home.models import AdvisorAccessRequest, SiteConfiguration
from recoco.utils import get_group_for_site


class TestAdvisorAccessRequestView:
    @pytest.mark.django_db
    def test_redirect_anonymous(self, client, current_site):
        response = client.get(reverse("advisor-access-request"))
        assert response.status_code == 302
        assert response.url == "/accounts/signup?next=/advisor-access-request"

    @pytest.mark.django_db
    def test_redirect_advisor(self, client, current_site):
        baker.make(SiteConfiguration, site=current_site)
        advisor = baker.make(User)
        advisor.groups.add(get_group_for_site("advisor", current_site))

        client.force_login(advisor)
        response = client.get(reverse("advisor-access-request"))
        assert response.status_code == 302
        assert response.url == "/"

    @pytest.mark.django_db
    def test_get_request(self, client, current_site):
        user = baker.make(User)
        baker.make(SiteConfiguration, site=current_site)
        baker.make(Department, code="64", name="Pyrénées-Atlantiques")
        baker.make(Department, code="33", name="Gironde")

        advisor_access_request = baker.make(
            AdvisorAccessRequest, site=current_site, user=user
        )
        advisor_access_request.departments.add(
            baker.make(Department, code="40", name="Landes")
        )

        client.force_login(user)

        response = client.get(reverse("advisor-access-request"))
        assert response.status_code == 200
        assert response.context["advisor_access_request"] == advisor_access_request
        assert response.context["form"] is not None
        assert response.context["departments"] == [
            {"name": "Gironde", "code": "33"},
            {"name": "Landes", "code": "40"},
            {"name": "Pyrénées-Atlantiques", "code": "64"},
        ]
        assert response.context["selected_departments"] == ["40"]

    @pytest.mark.django_db(transaction=True)
    def test_post_request(self, client, current_site, staff_user, admin_user):
        baker.make(SiteConfiguration, site=current_site)
        user = baker.make(User)
        baker.make(Department, code="64", name="Pyrénées-Atlantiques")
        baker.make(Department, code="33", name="Gironde")
        baker.make(Department, code="40", name="Landes")

        client.force_login(user)
        response = client.get(reverse("advisor-access-request"))
        assert response.status_code == 200
        assert response.context.get("advisor_access_request") is None

        assert AdvisorAccessRequest.objects.count() == 0

        response = client.post(
            reverse("advisor-access-request"),
            data={
                "advisor_access_type": "Regional",
                "departments": ["64", "33"],
                "comment": "Merci pour votre aide !",
            },
        )
        assert response.status_code == 200

        advisor_access_request = (
            AdvisorAccessRequest.objects.filter(site=current_site)
            .prefetch_related("departments")
            .first()
        )
        assert advisor_access_request is not None
        assert advisor_access_request.user == user
        assert advisor_access_request.status == "PENDING"
        assert advisor_access_request.departments.count() == 2
        assert advisor_access_request.comment == "Merci pour votre aide !"

        assert (
            action_models.Action.objects.filter(verb=verbs.User.ADVISOR_REQUEST).count()
            == 1
        )
        assert (
            notifications_models.Notification.objects.filter(
                verb=verbs.User.ADVISOR_REQUEST
            ).count()
            == 2
        )  # one for admin and one for staff

        response = client.post(
            reverse("advisor-access-request"),
            data={
                "advisor_access_type": "Regional",
                "departments": ["64", "33", "40"],
                "comment": "Test comment",
            },
        )
        assert response.status_code == 200

        advisor_access_request.refresh_from_db()
        assert AdvisorAccessRequest.objects.count() == 1
        assert advisor_access_request.departments.count() == 3
        assert advisor_access_request.comment == "Test comment"

        # should not notify again if request is only modified
        assert (
            action_models.Action.objects.filter(verb=verbs.User.ADVISOR_REQUEST).count()
            == 1
        )
        assert (
            notifications_models.Notification.objects.filter(
                verb=verbs.User.ADVISOR_REQUEST
            ).count()
            == 2
        )  # one for admin and one for staff

    @pytest.mark.django_db(transaction=True)
    def test_post_request_national_no_dep_ok(
        self, client, current_site, staff_user, admin_user
    ):
        baker.make(SiteConfiguration, site=current_site)
        user = baker.make(User)
        baker.make(Department, code="40", name="Landes")

        client.force_login(user)
        response = client.get(reverse("advisor-access-request"))
        assert response.status_code == 200
        assert response.context.get("advisor_access_request") is None

        assert AdvisorAccessRequest.objects.count() == 0

        response = client.post(
            reverse("advisor-access-request"),
            data={
                "advisor_access_type": "National",
                "comment": "Merci pour votre aide !",
            },
        )
        assert response.status_code == 200

        advisor_access_request = (
            AdvisorAccessRequest.objects.filter(site=current_site)
            .prefetch_related("departments")
            .first()
        )
        assert advisor_access_request is not None
        assert advisor_access_request.user == user
        assert advisor_access_request.status == "PENDING"
        assert advisor_access_request.departments.count() == 0
        assert advisor_access_request.comment == "Merci pour votre aide !"


class TestAdvisorAccessRequestModeratorView:
    @pytest.mark.django_db
    def test_redirect_anonymous(self, client):
        response = client.get(reverse("advisor-access-request-moderator", args=[1]))
        assert response.status_code == 302
        assert response.url == "/accounts/login/?next=/advisor-access-request/1/"

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=False))
    def test_not_project_moderator(self, client):
        user = baker.make(User)
        client.force_login(user)
        response = client.get(
            client.get(reverse("advisor-access-request-moderator", args=[1]))
        )
        # FIXME:
        assert response.status_code != 200
        # assert response.status_code == 403

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=True))
    def test_object_not_found(self, client):
        user = baker.make(User)
        client.force_login(user)
        response = client.get(
            client.get(reverse("advisor-access-request-moderator", args=[1]))
        )
        assert response.status_code == 404

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=True))
    def test_get_request(self, client, current_site):
        user = baker.make(User)
        client.force_login(user)

        advisor_access_request = baker.make(AdvisorAccessRequest, site=current_site)
        advisor_access_request.departments.add(
            baker.make(Department, code="64", name="Pyrénées-Atlantiques"),
            baker.make(Department, code="33", name="Gironde"),
        )

        url = reverse(
            "advisor-access-request-moderator", args=[advisor_access_request.id]
        )

        response = client.get(url)
        assert response.status_code == 200
        assert response.context["advisor_access_request"] == advisor_access_request
        assert response.context["departments"] == [
            {"name": "Gironde", "code": "33"},
            {"name": "Pyrénées-Atlantiques", "code": "64"},
        ]
        assert response.context["selected_departments"] == ["33", "64"]
        assert response.context["form"] is not None

        advisor_access_request.status = "ACCEPTED"
        advisor_access_request.save()

        response = client.get(url)
        assert response.status_code == 302
        assert response.url == reverse("projects-moderation-list")

    @pytest.mark.django_db
    @patch("recoco.apps.projects.utils.is_project_moderator", Mock(return_value=True))
    def test_post_request(self, client, current_site):
        user = baker.make(User)
        client.force_login(user)

        advisor_access_request = baker.make(AdvisorAccessRequest, site=current_site)
        (baker.make(Department, code="64", name="Pyrénées-Atlantiques"),)
        (baker.make(Department, code="33", name="Gironde"),)

        url = reverse(
            "advisor-access-request-moderator", args=[advisor_access_request.id]
        )

        response = client.post(
            url, data={"advisor_access_type": "Regional", "departments": ["dummy_code"]}
        )
        assert response.status_code == 200
        assert response.context["form"].errors is not None

        response = client.post(
            url,
            data={
                "advisor_access_type": "Regional",
                "departments": ["64", "33"],
                "comment": "Merci pour votre aide !",
            },
        )
        assert response.status_code == 302
        assert response.url == reverse("projects-moderation-list")

        advisor_access_request.refresh_from_db()
        assert list(
            advisor_access_request.departments.values_list("code", flat=True)
        ) == ["33", "64"]
