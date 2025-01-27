import pytest
from django.contrib.auth.models import User
from model_bakery import baker

from recoco.apps.addressbook.models import Contact
from recoco.apps.hitcount.models import Hit, HitCount
from recoco.apps.projects.models import Project
from recoco.apps.tasks.models import Task


@pytest.mark.django_db
def test_manager_queryset():
    contact = baker.make(Contact)
    project = baker.make(Project)
    resource = baker.make(Task)

    user_1 = baker.make(User)
    user_2 = baker.make(User)

    hitcount_contact_project = baker.make(
        HitCount, content_object=contact, context_object=project
    )
    baker.make(Hit, hitcount=hitcount_contact_project, user=user_1)
    baker.make(Hit, hitcount=hitcount_contact_project, user=user_2)

    hitcount_contact_resource = baker.make(
        HitCount, content_object=contact, context_object=resource
    )
    baker.make(Hit, hitcount=hitcount_contact_resource, user=user_1)

    assert HitCount.objects.for_content_object(contact).count() == 2

    queryset = HitCount.objects.for_context_object(project)
    assert queryset.count() == 1
    assert queryset.first() == hitcount_contact_project

    queryset = HitCount.objects.for_context_object(resource)
    assert queryset.count() == 1
    assert queryset.first() == hitcount_contact_resource

    assert HitCount.objects.for_user(user_1).count() == 2

    queryset = HitCount.objects.for_user(user_2)
    assert queryset.count() == 1
    assert queryset.first() == hitcount_contact_project

    queryset = HitCount.objects.for_user(user_1).for_context_object(resource)
    assert queryset.count() == 1
    assert queryset.first() == hitcount_contact_resource

    assert queryset.for_content_object(project).count() == 0
    assert queryset.for_content_object(contact).count() == 1
