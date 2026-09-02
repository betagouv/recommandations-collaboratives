import pytest
from django.contrib.auth.models import Group
from django.urls import reverse
from model_bakery import baker


@pytest.mark.django_db
def test_anonymous_can_not_read_feed(client):
    response = client.get(reverse("projects-feed"))
    assert response.status_code == 401


@pytest.mark.django_db
def test_random_cannot_access_feed(client):
    user = baker.make("User")
    client.force_login(user)
    response = client.get(reverse("projects-feed"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_advisor_can_access_feed(client, current_site, make_project):
    projects = [make_project(name=f"project-{i}") for i in range(6)]

    advisor = baker.make("User")
    advisor.profile.sites.add(current_site)
    group, _ = Group.objects.get_or_create(name="example_com_advisor")
    advisor.groups.add(group)

    client.force_login(advisor)

    response = client.get(reverse("projects-feed"))

    assert response.status_code == 200
    for project in projects[1:]:
        assert project.name in response.text
    assert projects[0].name not in response.text
