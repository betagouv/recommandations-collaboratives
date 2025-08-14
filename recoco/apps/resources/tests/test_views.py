# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-16 17:56:10 CEST
"""

from datetime import datetime

import pytest
import reversion
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects
from reversion.models import Version

from recoco.apps.addressbook.models import Contact
from recoco.apps.geomatics import models as geomatics
from recoco.apps.hitcount.models import Hit, HitCount
from recoco.apps.projects import models as projects_models
from recoco.apps.tasks.models import Task
from recoco.utils import login

from .. import models

########################################################################
# resources
########################################################################

#
# search / list


@pytest.mark.django_db
def test_resource_list_available_for_every_one(client):
    url = reverse("resources-resource-search")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_resource_list_contains_published_resource_title_and_link(request, client):
    resource = Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.PUBLISHED,
        title=" public resource",
    ).make()
    url = reverse("resources-resource-search")
    response = client.get(url)
    assertContains(response, resource.title)
    detail_url = reverse("resources-resource-detail", args=[resource.id])
    assertContains(response, detail_url)


@pytest.mark.django_db
def test_draft_resources_are_not_available_to_non_staff_users(request, client):
    resource = Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.DRAFT,
        title="draft resource",
    ).make()
    url = reverse("resources-resource-search")
    response = client.get(url)
    detail_url = reverse("resources-resource-detail", args=[resource.id])
    assertNotContains(response, detail_url)


@pytest.mark.django_db
def test_draft_resources_are_available_to_staff_users(request, client):
    resource = Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.DRAFT,
        title="a draft resource",
    ).make()
    url = reverse("resources-resource-search")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    detail_url = reverse("resources-resource-detail", args=[resource.id])
    assertContains(response, detail_url)


@pytest.mark.django_db
def test_resource_list_contains_only_resource_with_category(request, client):
    current_site = get_current_site(request)

    category1 = Recipe(models.Category, sites=[current_site]).make()
    resource1 = Recipe(
        models.Resource,
        sites=[current_site],
        title="selected resource",
        status=models.Resource.PUBLISHED,
        category=category1,
    ).make()
    category2 = Recipe(models.Category, sites=[current_site]).make()
    resource2 = Recipe(
        models.Resource,
        sites=[current_site],
        title="unselected resource",
        status=models.Resource.PUBLISHED,
        category=category2,
    ).make()
    url = reverse("resources-resource-search")
    url = f"{url}?cat{category1.id}=true&query=resource"
    response = client.get(url)
    detail_url = reverse("resources-resource-detail", args=[resource1.id])
    assertContains(response, detail_url)
    detail_url = reverse("resources-resource-detail", args=[resource2.id])
    assertNotContains(response, detail_url)


@pytest.mark.django_db
def test_resource_list_contains_only_resource_with_area(request, client):
    current_site = get_current_site(request)
    departments = Recipe(geomatics.Department).make(_quantity=3)
    resource1 = Recipe(
        models.Resource,
        sites=[current_site],
        title="selected resource",
        status=models.Resource.PUBLISHED,
        departments=departments[1:],
    ).make()
    resource2 = Recipe(
        models.Resource,
        sites=[current_site],
        title="unselected resource",
        status=models.Resource.PUBLISHED,
        departments=departments[:1],
    ).make()
    resource_national = Recipe(
        models.Resource,
        sites=[current_site],
        title="national resource",
        status=models.Resource.PUBLISHED,
    ).make()

    url = reverse("resources-resource-search")
    url = f"{url}?limit_area=true&query=resource"

    membership = baker.make(projects_models.ProjectMember)
    with login(client, user=membership.member):
        Recipe(
            projects_models.Project,
            sites=[current_site],
            projectmember_set=[membership],
            commune__department=departments[1],
        ).make()
        response = client.get(url)
    detail_url = reverse("resources-resource-detail", args=[resource1.id])
    assertContains(response, detail_url)
    detail_url = reverse("resources-resource-detail", args=[resource_national.id])
    assertContains(response, detail_url)
    detail_url = reverse("resources-resource-detail", args=[resource2.id])
    assertNotContains(response, detail_url)


@pytest.mark.django_db
def test_resource_list_contains_only_resource_with_draft_selected(request, client):
    current_site = get_current_site(request)

    resource1 = Recipe(
        models.Resource,
        sites=[current_site],
        title="selected resource",
        status=models.Resource.DRAFT,
    ).make()
    resource2 = Recipe(
        models.Resource,
        sites=[current_site],
        title="unselected resource",
        status=models.Resource.PUBLISHED,
    ).make()

    url = reverse("resources-resource-search")
    url = f"{url}?draft=true&query=resource"
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    detail_url = reverse("resources-resource-detail", args=[resource1.id])
    assertContains(response, detail_url)
    detail_url = reverse("resources-resource-detail", args=[resource2.id])
    assertNotContains(response, detail_url)


@pytest.mark.django_db
def test_resource_list_contains_only_resource_with_to_review_selected(request, client):
    current_site = get_current_site(request)

    resource1 = Recipe(
        models.Resource,
        sites=[current_site],
        title="selected resource",
        status=models.Resource.TO_REVIEW,
    ).make()
    resource2 = Recipe(
        models.Resource,
        sites=[current_site],
        title="unselected resource",
        status=models.Resource.PUBLISHED,
    ).make()

    url = reverse("resources-resource-search")
    url = f"{url}?to_review=true&query=resource"
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    detail_url = reverse("resources-resource-detail", args=[resource1.id])
    assertContains(response, detail_url)
    detail_url = reverse("resources-resource-detail", args=[resource2.id])
    assertNotContains(response, detail_url)


@pytest.mark.django_db
def test_resource_list_contains_only_resource_with_expired_selected(request, client):
    current_site = get_current_site(request)

    resource1 = Recipe(
        models.Resource,
        sites=[current_site],
        title="selected resource",
        status=models.Resource.PUBLISHED,
        expires_on="1970-01-01",
    ).make()
    resource2 = Recipe(
        models.Resource,
        sites=[current_site],
        title="unselected resource",
        status=models.Resource.PUBLISHED,
    ).make()

    url = reverse("resources-resource-search")
    url = f"{url}?expired=true&query=resource"
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    detail_url = reverse("resources-resource-detail", args=[resource1.id])
    assertContains(response, detail_url)
    detail_url = reverse("resources-resource-detail", args=[resource2.id])
    assertNotContains(response, detail_url)


@pytest.mark.django_db
def test_resource_list_contains_only_uncategorized(current_site, client):
    resource1 = Recipe(
        models.Resource,
        sites=[current_site],
        title="uncategorized resource",
        status=models.Resource.PUBLISHED,
        category=None,
    ).make()

    resource2 = Recipe(
        models.Resource,
        sites=[current_site],
        title="categorized resource",
        status=models.Resource.PUBLISHED,
        category__sites=[current_site],
    ).make()

    resource1_url = reverse("resources-resource-detail", args=[resource1.id])
    resource2_url = reverse("resources-resource-detail", args=[resource2.id])

    response = client.get(
        f"{reverse('resources-resource-search')}?no_category=true&query=resource"
    )
    assertContains(response, resource1_url)
    assertNotContains(response, resource2_url)

    response = client.get(
        f"{reverse('resources-resource-search')}?no_category=false&query=resource"
    )
    assertContains(response, resource2_url)
    assertContains(response, resource1_url)


@pytest.mark.django_db
def test_resource_list_contains_only_published(current_site, client):
    resource1 = Recipe(
        models.Resource,
        sites=[current_site],
        title="published resource",
        status=models.Resource.PUBLISHED,
    ).make()

    resource2 = Recipe(
        models.Resource,
        sites=[current_site],
        title="draft resource",
        status=models.Resource.DRAFT,
    ).make()

    response = client.get(
        f"{reverse('resources-resource-search')}?published=true&query=resource"
    )

    detail_url = reverse("resources-resource-detail", args=[resource1.id])
    assertContains(response, detail_url)
    detail_url = reverse("resources-resource-detail", args=[resource2.id])
    assertNotContains(response, detail_url)


#
# details


@pytest.mark.django_db
def test_public_resource_detail_available_for_all_users(request, client):
    resource = Recipe(
        models.Resource,
        status=models.Resource.PUBLISHED,
        sites=[get_current_site(request)],
        title="A Nice title",
    ).make()
    url = reverse("resources-resource-detail", args=[resource.id])
    response = client.get(url)

    assert response.status_code == 200
    assertContains(response, resource.title)


@pytest.mark.django_db
def test_draft_resource_visible_to_any_authenticated_user(request, client):
    site = get_current_site(request)
    resource = Recipe(
        models.Resource, sites=[site], status=models.Resource.DRAFT
    ).make()

    url = reverse("resources-resource-detail", args=[resource.id])

    response = client.get(url)
    assert response.status_code == 302

    with login(client):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_resource_detail_contains_update_for_authorized_user(request, client):
    site = get_current_site(request)
    resource = Recipe(models.Resource, sites=[site]).make()
    url = reverse("resources-resource-detail", args=[resource.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    update_url = reverse("resources-resource-update", args=[resource.id])
    assertContains(response, update_url)


@pytest.mark.django_db
def test_resource_detail_does_not_contain_update_for_common_user(request, client):
    resource = Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.PUBLISHED,
    ).make()
    url = reverse("resources-resource-detail", args=[resource.id])
    with login(client):
        response = client.get(url)
    update_url = reverse("resources-resource-update", args=[resource.id])
    assertNotContains(response, update_url)


@pytest.mark.django_db
def test_resource_detail_contacts_to_display(request, client):
    site = get_current_site(request)
    resource = Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
    ).make()

    contact = baker.make(Contact)

    url = reverse("resources-resource-detail", args=[resource.id])

    with login(client) as user:
        response = client.get(url)
        assert response.context["contacts_to_display"] == []

        hitcount = baker.make(
            HitCount, site=site, content_object=contact, context_object=resource
        )
        baker.make(Hit, hitcount=hitcount, user=user)

        response = client.get(url)
        assert response.context["contacts_to_display"] == [contact.id]


#
# create


@pytest.mark.resource_create
@pytest.mark.django_db
def test_create_resource_not_available_for_non_switchtender_users(client):
    url = reverse("resources-resource-create")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.resource_create
@pytest.mark.django_db
def test_create_resource_available_for_authorized_users(client):
    url = reverse("resources-resource-create")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-resource-create"')


@pytest.mark.resource_create
@pytest.mark.django_db
def test_create_new_resource_and_redirect(request, client):
    data = {
        "title": "a title",
        "subtitle": "a sub title",
        "status": 0,
        "summary": "a summary",
        "tags": "#tag",
        "content": "this is some content",
    }

    with login(client, groups=["example_com_staff"]):
        response = client.post(reverse("resources-resource-create"), data=data)

    assert response.status_code == 302

    resource = models.Resource.on_site.all()[0]
    assert resource.content == data["content"]
    assert resource.site_origin == get_current_site(request)


########################################################################
# update
########################################################################


@pytest.mark.resource_update
@pytest.mark.django_db
def test_update_resource_not_available_for_non_staff(request, client):
    resource = Recipe(models.Resource, sites=[get_current_site(request)]).make()

    url = reverse("resources-resource-update", args=[resource.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.resource_update
@pytest.mark.django_db
def test_update_resource_available_for_staff(request, client):
    resource = Recipe(models.Resource, sites=[get_current_site(request)]).make()

    url = reverse("resources-resource-update", args=[resource.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, 'form id="form-resource-update"')


@pytest.mark.resource_update
@pytest.mark.django_db
def test_update_resource_from_origin_site_and_redirect(request, client):
    resource = baker.make(models.Resource)
    current_site = get_current_site(request)
    resource.site_origin = current_site
    resource.save()

    previous_update = resource.updated_on

    url = reverse("resources-resource-update", args=[resource.id])

    data = {
        "title": "a title",
        "subtitle": "a sub title",
        "status": 0,
        "summary": "a summary",
        "tags": "#tag",
        "content": "this is some updated content",
    }

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    assert response.status_code == 302

    resource.refresh_from_db()
    assert resource.content == data["content"]
    assert resource.updated_on > previous_update


@pytest.mark.resource_update
@pytest.mark.django_db
def test_update_resource_from_non_origin_site_does_not_duplicate_with_get(
    request, client
):
    original_resource = baker.make(models.Resource)
    current_site = get_current_site(request)
    other_site = baker.make(Site)

    original_resource.sites.add(current_site, other_site)
    original_resource.site_origin = other_site

    original_resource.save()

    assert models.Resource.objects.all().count() == 1

    url = reverse("resources-resource-update", args=[original_resource.id])

    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200
    assert models.Resource.objects.all().count() == 1


@pytest.mark.resource_update
@pytest.mark.django_db
def test_update_resource_from_non_origin_site_with_invalid_form(request, client):
    original_resource = baker.make(models.Resource)
    current_site = get_current_site(request)
    other_site = baker.make(Site)

    original_resource.sites.add(current_site, other_site)
    original_resource.site_origin = other_site
    previous_update = timezone.now()
    original_resource.updated_on = previous_update
    original_content = "this is some original content"
    original_resource.content = original_content

    original_resource.save()

    assert models.Resource.objects.all().count() == 1

    url = reverse("resources-resource-update", args=[original_resource.id])

    bad_data = {
        "titl": 1,
        "subtitl": 2,
        "statu": 0,
        "summar": "a summary",
        "tag": "#tag",
        "conten": "this is some badly formatted content",
    }

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=bad_data)

    assert response.status_code == 200

    assert original_resource.content == original_content
    assert models.Resource.objects.all().count() == 1


@pytest.mark.resource_update
@pytest.mark.django_db
def test_update_resource_from_non_origin_site_and_redirect(request, client):
    original_resource = baker.make(models.Resource)
    current_site = get_current_site(request)
    other_site = baker.make(Site)
    additional_site = baker.make(Site)

    original_resource.sites.add(current_site, other_site, additional_site)
    original_resource.site_origin = other_site
    previous_update = timezone.now()
    original_resource.updated_on = previous_update
    original_content = "this is some original content"
    original_resource.content = original_content
    original_resource.tags.add("tag1")
    original_resource.tags.add("tag2")

    original_resource.save()

    assert models.Resource.objects.all().count() == 1

    url = reverse("resources-resource-update", args=[original_resource.id])

    updated_data = {
        "title": "a title",
        "subtitle": "a sub title",
        "status": 0,
        "summary": "a summary",
        "content": "this is some updated content",
        "tags": "tag2",
    }

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=updated_data)

    assert response.status_code == 302

    original_resource.refresh_from_db()
    assert original_resource.content == original_content
    assert original_resource.updated_on == previous_update
    assert other_site in original_resource.sites.all()
    assert additional_site in original_resource.sites.all()
    assert current_site not in original_resource.sites.all()
    assert original_resource.site_origin == other_site
    assert original_resource.sites.count() == 2

    new_resource = models.Resource.on_site.get()
    assert new_resource != original_resource
    assert new_resource.content == updated_data["content"]
    assert other_site not in new_resource.sites.all()
    assert additional_site not in new_resource.sites.all()
    assert new_resource.sites.count() == 1
    assert current_site in new_resource.sites.all()
    assert new_resource.tags.get().name == "tag2"
    assert new_resource.site_origin == current_site


########################################################################
# delete
########################################################################


@pytest.mark.resource_delete
@pytest.mark.django_db
def test_delete_resource_not_available_for_non_staff_users(client, request):
    resource = baker.make(models.Resource)
    current_site = get_current_site(request)
    resource.sites.add(current_site)

    url = reverse("resources-resource-delete", args=[resource.pk])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.resource_delete
@pytest.mark.django_db
def test_delete_resource_referenced_available_for_staff(client, request):
    resource = baker.make(models.Resource)
    current_site = get_current_site(request)
    resource.sites.add(current_site)

    url = reverse("resources-resource-delete", args=(resource.pk,))
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, 'form id="form-resource-delete"')
    assert models.Resource.objects.all().count() == 1


@pytest.mark.resource_delete
@pytest.mark.django_db
def test_delete_resource_shared_and_redirect(client, request):
    resource = baker.make(models.Resource)
    current_site = get_current_site(request)
    other_site = baker.make(Site)
    resource.sites.add(current_site)
    resource.sites.add(other_site)

    assert resource.sites.count() == 2

    url = reverse("resources-resource-delete", args=(resource.pk,))
    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 302

    resource.refresh_from_db()
    assert resource.sites.count() == 1
    assert current_site not in resource.sites.all()
    assert other_site in resource.sites.all()
    assert resource.deleted is None


@pytest.mark.resource_delete
@pytest.mark.django_db
def test_delete_resource_non_shared_and_redirect(client, request):
    resource = baker.make(models.Resource)
    current_site = get_current_site(request)
    resource.sites.add(current_site)

    assert resource.sites.count() == 1

    url = reverse("resources-resource-delete", args=(resource.pk,))
    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 302

    resource.refresh_from_db()
    assert resource.sites.count() == 0
    assert resource.deleted is not None


#
# history
@pytest.mark.django_db
def test_resource_history_not_available_for_common_user(request, client):
    resource = Recipe(models.Resource, sites=[get_current_site(request)]).make()
    url = reverse("resources-resource-history", args=[resource.id])
    with login(client):
        response = client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
def test_resource_history_available_for_authorized_user(request, client):
    resource = Recipe(models.Resource, sites=[get_current_site(request)]).make()
    url = reverse("resources-resource-history", args=[resource.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
def test_resource_history_reversion_not_available_for_common_user(request, client):
    resource = Recipe(models.Resource, sites=[get_current_site(request)]).make()
    url = reverse("resources-resource-history-restore", args=[resource.id, 2])
    with login(client):
        response = client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
def test_resource_history_creates_revision(request, client):
    resource = Recipe(
        models.Resource,
        category__sites=[get_current_site(request)],
        sites=[get_current_site(request)],
    ).make()

    url = reverse("resources-resource-update", args=[resource.id])

    data = {
        "title": "a title",
        "subtitle": "a sub title",
        "status": 0,
        "summary": "a summary",
        "tags": "#tag",
        "content": "this is some content",
    }

    with login(client, groups=["example_com_staff"]):
        client.post(url, data=data)

    assert Version.objects.get_for_object(resource).count() == 1


@pytest.mark.django_db
def test_resource_history_reversion_available_for_authorized_user(request, client):
    resource = Recipe(
        models.Resource,
        title="first",
        category__sites=[get_current_site(request)],
        sites=[get_current_site(request)],
    ).make()

    with transaction.atomic(), reversion.create_revision():
        resource.save()

    with transaction.atomic(), reversion.create_revision():
        resource.title = "hello"
        resource.save()

    assert Version.objects.get_for_object(resource).count() == 2
    version = Version.objects.get_for_object(resource).last()

    url = reverse("resources-resource-history-restore", args=[resource.id, version.pk])
    with login(client, groups=["example_com_staff"]):
        response = client.post(url)
        assert response.status_code == 302

    resource.refresh_from_db()

    assert resource.title == "first"
    assert Version.objects.get_for_object(resource).count() == 3


########################################################################
# Resource searching
########################################################################


@pytest.mark.django_db
def test_search_resources_without_query(request):
    resource = Recipe(models.Resource, sites=[get_current_site(request)]).make()
    unmatched = models.Resource.search()
    assert resource in unmatched


@pytest.mark.django_db
def test_search_resources_do_not_match_query(request):
    resource = Recipe(models.Resource, sites=[get_current_site(request)]).make()
    unmatched = models.Resource.search(query="notfound")
    assert resource not in unmatched


@pytest.mark.django_db
def test_search_resources_by_tag(request):
    resource = Recipe(models.Resource, sites=[get_current_site(request)]).make()
    resource.tags.add("atag")
    resource.save()

    matched = models.Resource.search(query="atag")
    assert resource in matched


@pytest.mark.django_db
def test_search_resources_by_summary(request):
    resource = Recipe(
        models.Resource, sites=[get_current_site(request)], summary="a summary"
    ).make()
    matched = models.Resource.search(query="summa")
    assert resource in matched


@pytest.mark.django_db
def test_search_resources_by_title(request):
    resource = Recipe(
        models.Resource, sites=[get_current_site(request)], title="a title"
    ).make()
    matched = models.Resource.search(query="titl")
    assert resource in matched


@pytest.mark.django_db
def test_search_resources_by_content(request):
    resource = Recipe(
        models.Resource, sites=[get_current_site(request)], content="some content..."
    ).make()
    matched = models.Resource.search(query="cont")
    assert resource in matched


@pytest.mark.django_db
def test_search_resources_by_category(request):
    # categories are search like: any category that fits
    categories = [
        Recipe(models.Category, sites=[get_current_site(request)]).make(),
        Recipe(models.Category, sites=[get_current_site(request)]).make(),
    ]
    resources = [
        Recipe(
            models.Resource, sites=[get_current_site(request)], category=category
        ).make()
        for category in categories
    ]
    matched = models.Resource.search(categories=categories)
    assert set(resources) == set(matched)


########################################################################
# Bookmarking a resource
########################################################################


@pytest.mark.django_db
def test_user_has_access_to_page_for_bookmark_with_notes(request, client):
    resource = Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.PUBLISHED,
    ).make()

    url = reverse("resources-bookmark-create", args=[resource.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 200
    # assertContains(response, 'form id="form-create-bookmark"')


@pytest.mark.django_db
def test_user_bookmarks_a_resource(request, client):
    resource = Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.PUBLISHED,
    ).make()

    url = reverse("resources-bookmark-create", args=[resource.id])
    with login(client) as user:
        data = {"comments": "some nice comments"}
        response = client.post(url, data=data)

    # a new bookmark is created
    bookmark = models.Bookmark.objects.all()[0]
    assert bookmark.created_by == user
    assert bookmark.resource == resource
    assert bookmark.comments == data["comments"]
    # user is redirected to resource details
    newurl = reverse("resources-resource-detail", args=[resource.id])
    assertRedirects(response, newurl)


@pytest.mark.django_db
def test_user_refresh_bookmark_of_a_resource(request, client):
    with login(client) as user:
        bookmark = Recipe(
            models.Bookmark,
            site=get_current_site(request),
            created_by=user,
            deleted=datetime.now(),
            resource__status=models.Resource.PUBLISHED,
        ).make()
        url = reverse("resources-bookmark-create", args=[bookmark.resource_id])
        data = {"comments": "some nice comments"}
        response = client.post(url, data=data)

    # existing deleted bookmark is reactivated
    updated_bookmark = models.Bookmark.objects.all()[0]
    assert updated_bookmark == bookmark
    assert updated_bookmark.comments == data["comments"]
    # user is redirected to resource details
    newurl = reverse("resources-resource-detail", args=[bookmark.resource_id])
    assertRedirects(response, newurl)


@pytest.mark.django_db
def test_user_deletes_a_personal_bookmark(request, client):
    with login(client) as user:
        bookmark = Recipe(
            models.Bookmark,
            site=get_current_site(request),
            created_by=user,
            resource__status=models.Resource.PUBLISHED,
        ).make()
        url = reverse("resources-bookmark-delete", args=[bookmark.resource_id])
        response = client.post(url)

    bookmark = models.Bookmark.deleted_on_site.get(id=bookmark.id)
    assert bookmark.deleted
    newurl = reverse("resources-resource-detail", args=[bookmark.resource_id])
    assertRedirects(response, newurl)


@pytest.mark.django_db
def test_user_cannot_delete_someone_else_bookmark(request, client):
    bookmark = Recipe(
        models.Bookmark,
        resource__status=models.Resource.PUBLISHED,
        site=get_current_site(request),
    ).make()
    url = reverse("resources-bookmark-delete", args=[bookmark.resource_id])

    with login(client):
        response = client.post(url)

    bookmark = models.Bookmark.on_site.get(id=bookmark.id)
    assert not bookmark.deleted
    newurl = reverse("resources-resource-detail", args=[bookmark.resource_id])
    assertRedirects(response, newurl)


################################################################################
# Multisite
################################################################################


@pytest.mark.django_db
def test_search_resources_honors_multisite(request):
    other_site = Recipe(Site).make()
    current_site = get_current_site(request)
    my_resource = Recipe(models.Resource, sites=[current_site]).make()
    other_resource = Recipe(models.Resource, sites=[other_site]).make()
    result = models.Resource.search()
    assert my_resource in result
    assert other_resource not in result


@pytest.mark.django_db
def test_category_honors_multisite(request):
    other_site = Recipe(Site).make()
    current_site = get_current_site(request)
    my_category = Recipe(models.Category, sites=[current_site]).make()
    other_category = Recipe(models.Category, sites=[other_site]).make()
    result = models.Category.on_site.all()
    assert my_category in result
    assert other_category not in result


@pytest.mark.django_db
def test_bookmark_honors_multisite(request):
    other_site = Recipe(Site).make()
    current_site = get_current_site(request)
    my_bookmark = Recipe(models.Bookmark, site=current_site).make()
    other_bookmark = Recipe(models.Bookmark, site=other_site).make()
    result = models.Bookmark.on_site.all()
    assert my_bookmark in result
    assert other_bookmark not in result


@pytest.mark.django_db
def test_deleted_bookmark_honors_multisite(request):
    other_site = Recipe(Site).make()
    current_site = get_current_site(request)
    my_bookmark = Recipe(
        models.Bookmark, site=current_site, deleted="2022-03-10"
    ).make()
    other_bookmark = Recipe(
        models.Bookmark, site=other_site, deleted="2022-03-10"
    ).make()
    result = models.Bookmark.deleted_on_site.all()
    assert my_bookmark in result
    assert other_bookmark not in result


#
# Embedded resource view


@pytest.mark.django_db
def test_embedded_resource_detail_view_with_task_context(client, request):
    resource = Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.PUBLISHED,
    ).make()

    task = Recipe(Task, resource=resource).make()

    response = client.get(
        path="{}?task_id={}".format(
            reverse("resources-resource-detail-embeded", args=[resource.id]),
            task.id,
        )
    )
    assert response.status_code == 200
    assert response.context["task"] == task
    assert response.context["contacts_to_display"] == []


@pytest.mark.django_db
def test_embedded_resource_detail_contacts_to_display(request, client):
    site = get_current_site(request)

    resource = Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
    ).make()

    task = Recipe(Task, resource=resource).make()

    contact = baker.make(Contact)

    url = f"{reverse('resources-resource-detail-embeded', args=[resource.id])}?task_id={task.id}"

    with login(client) as user:
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["contacts_to_display"] == []

        hitcount = baker.make(
            HitCount, site=site, content_object=contact, context_object=resource
        )
        baker.make(Hit, hitcount=hitcount, user=user)

        response = client.get(url)
        assert response.context["contacts_to_display"] == [contact.id]


# eof
