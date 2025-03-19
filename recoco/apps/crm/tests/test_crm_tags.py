import pytest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker

from recoco.apps.addressbook.models import Contact, Organization
from recoco.apps.crm.models import Note
from recoco.apps.crm.templatetags.crm_tags import get_note_update_url
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


@pytest.mark.django_db
def test_site_configuration_tags():
    pass
    # TODO: test siteconfiguration_tags
