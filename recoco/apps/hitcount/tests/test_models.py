import pytest
from model_bakery import baker

from recoco.apps.addressbook.models import Contact
from recoco.apps.hitcount.models import HitCount
from recoco.apps.projects.models import Project


@pytest.mark.django_db
def test_hitcount_str():
    contact = baker.make(Contact)
    hitcount = baker.make(HitCount, content_object=contact)
    assert str(hitcount) == f"contact-{contact.id}"

    project = baker.make(Project)
    hitcount.context_object = project
    hitcount.save()
    assert str(hitcount) == f"contact-{contact.id} (project-{project.id})"
