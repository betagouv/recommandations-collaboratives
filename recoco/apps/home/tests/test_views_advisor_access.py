import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from model_bakery import baker

from recoco.apps.geomatics.models import Department
from recoco.apps.home.models import AdvisorAccessRequest
from recoco.utils import get_group_for_site


class TestAdvisorAccessRequestView:
    @pytest.mark.django_db
    def test_redirect_anonymous(self, client, current_site):
        response = client.get(reverse("advisor-access-request"))
        assert response.status_code == 302
        assert response.url == "/accounts/login/?next=/advisor-access-request"

    @pytest.mark.django_db
    def test_redirect_advisor(self, client, current_site):
        advisor = baker.make(User)
        advisor.groups.add(get_group_for_site("advisor", current_site))

        client.force_login(advisor)
        response = client.get(reverse("advisor-access-request"))
        assert response.status_code == 302
        assert response.url == "/"

    @pytest.mark.django_db(transaction=True)
    def test_advisor_access_request(self, client, current_site):
        user = baker.make(User)
        baker.make(Department, code="64", name="Pyrénées-Atlantiques")
        baker.make(Department, code="33", name="Gironde")

        client.force_login(user)
        response = client.get(reverse("advisor-access-request"))
        assert response.status_code == 200
        assert response.context.get("advisor_access_request") is None

        assert AdvisorAccessRequest.objects.count() == 0

        response = client.post(
            reverse("advisor-access-request"),
            data={"departments": ["64", "33"]},
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
