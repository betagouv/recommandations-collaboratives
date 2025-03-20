import pytest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker

from recoco.apps.addressbook.models import Contact, Organization
from recoco.apps.crm.models import Note, ProjectAnnotations
from recoco.apps.crm.templatetags.crm_tags import get_note_update_url
from recoco.apps.home.models import SiteConfiguration
from recoco.apps.projects.models import Project


@pytest.mark.django_db
def test_get_note_update_url():
    note = baker.prepare(Note, id=1, object_id=2)

    note.content_type = ContentType.objects.get_for_model(User)
    assert get_note_update_url(note) == "/crm/user/2/note/1"

    note.content_type = ContentType.objects.get_for_model(Organization)
    assert get_note_update_url(note) == "/crm/org/2/note/1"

    note.content_type = ContentType.objects.get_for_model(Project)
    assert get_note_update_url(note) == "/crm/project/2/note/1"

    note.content_type = ContentType.objects.get_for_model(Contact)
    assert get_note_update_url(note) is None


@pytest.fixture()
def current_site_with_config(current_site):
    site_config = baker.make(SiteConfiguration, site=current_site)
    site_config.crm_available_tags.add("tag_one", "tag_two")
    yield current_site


@pytest.mark.django_db
class TestViewSiteConfigurationTags:
    url = reverse("crm-site-configuration-tags")

    def test_view_perms(self, client, current_site_with_config):
        user = baker.make(User)
        client.force_login(user)

        response = client.get(self.url)
        assert response.status_code == 403

        assign_perm("manage_configuration", user, current_site_with_config)

        response = client.get(self.url)
        assert response.status_code == 200
        assert [tag.name for tag in response.context["tags"]] == [
            "tag_one",
            "tag_two",
        ]
        assert list(
            current_site_with_config.configuration.crm_available_tags.names()
        ) == [
            "tag_one",
            "tag_two",
        ]

    def test_post_add_tag(self, client, current_site_with_config):
        user = baker.make(User)
        assign_perm("manage_configuration", user, current_site_with_config)
        client.force_login(user)

        response = client.post(
            self.url,
            headers={"HX_REQUEST": "true"},
            data={"action": "add", "new_tag_name": "tag_three"},
        )
        assert response.status_code == 200
        assert [tag.name for tag in response.context["tags"]] == [
            "tag_one",
            "tag_three",
            "tag_two",
        ]

    def test_post_remove_tag(self, client, current_site_with_config):
        user = baker.make(User)
        assign_perm("manage_configuration", user, current_site_with_config)
        client.force_login(user)

        project = baker.make(Project, sites=[current_site_with_config])
        project_annotations = baker.make(
            ProjectAnnotations, project=project, site=current_site_with_config
        )
        project_annotations.tags.add("tag_one", "tag_two")

        response = client.post(
            self.url,
            headers={"HX_REQUEST": "true"},
            data={"action": "remove", "tag_name": "tag_one"},
        )
        assert response.status_code == 200
        assert [tag.name for tag in response.context["tags"]] == ["tag_two"]
        assert list(project.crm_annotations.tags.names()) == ["tag_two"]
        assert list(
            current_site_with_config.configuration.crm_available_tags.names()
        ) == ["tag_two"]

    def test_post_rename_tag(self, client, current_site_with_config):
        user = baker.make(User)
        assign_perm("manage_configuration", user, current_site_with_config)
        client.force_login(user)

        project = baker.make(Project, sites=[current_site_with_config])
        project_annotations = baker.make(
            ProjectAnnotations, project=project, site=current_site_with_config
        )
        project_annotations.tags.add("tag_one")

        response = client.post(
            self.url,
            headers={"HX_REQUEST": "true"},
            data={
                "action": "rename",
                "tag_name": "tag_one",
                "new_tag_name": "tag_azou",
            },
        )
        assert response.status_code == 200
        assert [tag.name for tag in response.context["tags"]] == ["tag_azou", "tag_two"]
        assert list(project.crm_annotations.tags.names()) == ["tag_azou"]
        assert list(
            current_site_with_config.configuration.crm_available_tags.names()
        ) == ["tag_azou", "tag_two"]
