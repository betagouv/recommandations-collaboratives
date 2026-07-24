# encoding: utf-8

"""
Tests for resources rest API

authors: sebastien.reuiller@beta.gouv.fr
created: 2024-02-05 17:11:56 CEST
"""

import datetime
import json

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery.recipe import Recipe, baker
from reversion.models import Version

from recoco.apps.projects import models as project_models
from recoco.apps.tasks import models as task_models

from .. import models
from ..serializers import ResourceWritableSerializer

########################################################################
# list of resources
########################################################################


@pytest.mark.django_db
def test_anonymous_can_see_resources_list_api(request, api_client):
    resource = Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.PUBLISHED,
        title=" public resource",
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["results"][0]["title"] == resource.title


@pytest.mark.django_db
def test_resources_list_does_not_include_content(request, api_client):
    Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.PUBLISHED,
        title=" public resource",
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url)
    assert response.status_code == 200

    assert "content" not in response.data["results"][0]


@pytest.mark.django_db
def test_resource_details_includes_content(request, api_client):
    resource = Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.PUBLISHED,
        title=" public resource",
    ).make()

    url = reverse("resources-detail", args=(resource.pk,))
    response = api_client.get(url)
    assert response.status_code == 200

    assert "content" in response.data


@pytest.mark.django_db
def test_resource_details_includes_nb_uses(request, api_client, current_site):
    resource = Recipe(
        models.Resource,
        sites=[current_site],
        status=models.Resource.PUBLISHED,
        title=" public resource",
    ).make()
    Recipe(task_models.Task, resource=resource, site=current_site).make()

    url = reverse("resources-detail", args=(resource.pk,))
    response = api_client.get(url)
    assert response.status_code == 200

    assert "nb_uses" in response.data
    assert response.data["nb_uses"] == 1


@pytest.mark.django_db
def test_resource_details_nb_uses_no_exclude_stats_projects(
    request, api_client, current_site
):
    resource = Recipe(
        models.Resource,
        sites=[current_site],
        status=models.Resource.PUBLISHED,
        title=" public resource",
    ).make()
    project = Recipe(project_models.Project, exclude_stats=True).make()
    Recipe(
        task_models.Task,
        resource=resource,
        site=current_site,
        project=project,
    ).make()

    url = reverse("resources-detail", args=(resource.pk,))
    response = api_client.get(url)
    assert "nb_uses" in response.data
    assert response.data["nb_uses"] == 0


@pytest.mark.django_db
def test_resource_details_nb_uses_no_foreign_sites(request, api_client, current_site):
    site = Recipe(Site).make()
    resource = Recipe(
        models.Resource,
        sites=[current_site, site],
        status=models.Resource.PUBLISHED,
        title="public resource",
    ).make()
    Recipe(
        task_models.Task,
        resource=resource,
        site=site,
    ).make()

    url = reverse("resources-detail", args=(resource.pk,))
    response = api_client.get(url)
    assert "nb_uses" in response.data
    assert response.data["nb_uses"] == 0


@pytest.mark.django_db
def test_anonymous_cannot_see_unpublished_resource_in_list_api(request, api_client):
    Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.TO_REVIEW,
        title=" to review resource",
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 0


@pytest.mark.django_db
def test_staff_can_see_unpublished_resource_in_list_api(request, api_client):
    site = get_current_site(request)
    resource = Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.TO_REVIEW,
        title=" to review resource",
    ).make()

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)

    url = reverse("resources-list")
    api_client.force_authenticate(user=staff)
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["title"] == resource.title


@pytest.mark.django_db
def test_resource_list_includes_nb_uses(request, api_client, current_site):
    resource = Recipe(
        models.Resource,
        sites=[current_site],
        status=models.Resource.PUBLISHED,
        title=" public resource",
    ).make()
    Recipe(task_models.Task, resource=resource, site=current_site).make()
    Recipe(task_models.Task, resource=resource, site=current_site).make()

    url = reverse("resources-list")
    response = api_client.get(url)
    assert response.status_code == 200

    assert "nb_uses" in response.data["results"][0]
    assert response.data["results"][0]["nb_uses"] == 2


@pytest.mark.django_db
def test_resource_list_nb_uses_no_exclude_stats_projects(
    request, api_client, current_site
):
    resource = Recipe(
        models.Resource,
        sites=[current_site],
        status=models.Resource.PUBLISHED,
        title=" public resource",
    ).make()
    project = Recipe(project_models.Project, exclude_stats=True).make()
    Recipe(
        task_models.Task,
        resource=resource,
        site=current_site,
        project=project,
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url)
    assert "nb_uses" in response.data["results"][0]
    assert response.data["results"][0]["nb_uses"] == 0


@pytest.mark.django_db
def test_resource_list_nb_uses_no_foreign_sites(request, api_client, current_site):
    site = Recipe(Site).make()
    resource = Recipe(
        models.Resource,
        sites=[current_site, site],
        status=models.Resource.PUBLISHED,
        title="public resource",
    ).make()
    Recipe(
        task_models.Task,
        resource=resource,
        site=site,
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url)
    assert "nb_uses" in response.data["results"][0]
    assert response.data["results"][0]["nb_uses"] == 0


@pytest.mark.django_db
def test_simple_user_cannot_create_resource_with_api(request, api_client):
    site = get_current_site(request)

    user = baker.make(auth_models.User)
    user.profile.sites.add(site)

    url = reverse("resources-list")
    api_client.force_authenticate(user=user)

    data = {
        "title": "one resource",
        "subtitle": "one resource to test",
        "status": 1,
        "tags": ["a tag"],
    }
    response = api_client.post(url, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_staff_user_can_create_resource_with_api(request, api_client):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_advisor")
    staff.groups.add(gstaff)

    category = baker.make(models.Category)

    url = reverse("resources-list")
    api_client.force_authenticate(user=staff)

    data = {
        "title": "one resource",
        "subtitle": "one resource to test",
        "status": 1,
        "tags": ["a tag"],
        "content": "toto",
        "category": category.id,
    }
    response = api_client.post(url, data=data)

    assert response.status_code == 201
    assert response.data["title"] == data["title"]
    assert response.data["created_by"]["first_name"] == staff.first_name
    assert response.data["created_by"]["last_name"] == staff.last_name


@pytest.mark.django_db
def test_staff_user_can_edit_resource_with_api(request, api_client):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_advisor")
    staff.groups.add(gstaff)
    other_user = baker.make(auth_models.User)

    resource = baker.make(
        models.Resource,
        title="titre",
        content="blabla",
        sites=[site],
        created_by=other_user,
    )
    category = baker.make(models.Category)

    url = reverse("resources-detail", args=[resource.pk])
    api_client.force_authenticate(user=staff)

    data = {
        "title": "one resource",
        "subtitle": "one resource to test",
        "status": 1,
        "tags": ["a tag"],
        "content": "toto",
        "category": category.id,
    }
    response = api_client.put(url, data=data)

    assert response.status_code == 200
    assert response.data["title"] == data["title"]
    assert response.data["created_by"]["first_name"] == resource.created_by.first_name
    assert response.data["created_by"]["last_name"] == resource.created_by.last_name


########################################################################
# filters and search
########################################################################


@pytest.mark.django_db
def test_filter_resources_by_category(request, api_client):
    site = get_current_site(request)
    cat_a = baker.make(models.Category, sites=[site])
    cat_b = baker.make(models.Category, sites=[site])

    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=cat_a,
        title="Resource A",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=cat_b,
        title="Resource B",
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url, {"category": cat_a.pk})
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["title"] == "Resource A"


@pytest.mark.django_db
def test_filter_resources_by_multiple_categories(request, api_client):
    site = get_current_site(request)
    cat_a = baker.make(models.Category, sites=[site])
    cat_b = baker.make(models.Category, sites=[site])
    cat_c = baker.make(models.Category, sites=[site])

    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=cat_a,
        title="Resource A",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=cat_b,
        title="Resource B",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=cat_c,
        title="Resource C",
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url, {"category": [cat_a.pk, cat_b.pk]})
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 2
    titles = {r["title"] for r in results}
    assert titles == {"Resource A", "Resource B"}


@pytest.mark.django_db
def test_filter_resources_by_single_status(request, api_client):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)

    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.DRAFT,
        title="Draft resource",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        title="Published resource",
    ).make()

    url = reverse("resources-list")
    api_client.force_authenticate(user=staff)
    response = api_client.get(url, {"status": models.Resource.DRAFT})
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["title"] == "Draft resource"


@pytest.mark.django_db
def test_filter_resources_by_multiple_statuses(request, api_client):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)

    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.DRAFT,
        title="Draft resource",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.TO_REVIEW,
        title="To review resource",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        title="Published resource",
    ).make()

    url = reverse("resources-list")
    api_client.force_authenticate(user=staff)
    response = api_client.get(
        url, {"status": [models.Resource.DRAFT, models.Resource.TO_REVIEW]}
    )
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 2
    titles = {r["title"] for r in results}
    assert titles == {"Draft resource", "To review resource"}


@pytest.mark.django_db
def test_filter_resources_combined_category_and_status(request, api_client):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)

    cat = baker.make(models.Category, sites=[site])

    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=cat,
        title="Published in category",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.DRAFT,
        category=cat,
        title="Draft in category",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=None,
        title="Published no category",
    ).make()

    url = reverse("resources-list")
    api_client.force_authenticate(user=staff)
    response = api_client.get(
        url, {"category": cat.pk, "status": models.Resource.PUBLISHED}
    )
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["title"] == "Published in category"


@pytest.mark.django_db
def test_search_resources_with_watson(request, api_client):
    site = get_current_site(request)

    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        title="Urbanisme durable",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        title="Mobilité douce",
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url, {"search": "urbanisme"})
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["title"] == "Urbanisme durable"


@pytest.mark.django_db
def test_search_resources_combined_with_filters(request, api_client):
    site = get_current_site(request)
    cat = baker.make(models.Category, sites=[site])

    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=cat,
        title="Urbanisme durable",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=None,
        title="Urbanisme ancien",
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url, {"search": "urbanisme", "category": cat.pk})
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["title"] == "Urbanisme durable"


########################################################################
# revisions / patch proposals
########################################################################


class TestRessourcePatches:
    @pytest.mark.django_db
    def test_patch_proposal_creates_revision_with_proposed_values(
        self, request, api_client
    ):
        """A modification proposal (as_patch) creates a pending revision holding
        the proposed values, while leaving the live resource untouched.

        Proposing a patch only requires being authenticated (no manage_resources).
        """
        site = get_current_site(request)

        user = baker.make(auth_models.User)
        user.profile.sites.add(site)

        old_category = baker.make(models.Category, sites=[site])
        new_category = baker.make(models.Category, sites=[site])

        resource = baker.make(
            models.Resource,
            sites=[site],
            site_origin=site,
            status=models.Resource.PUBLISHED,
            title="ancien titre",
            subtitle="ancien sous-titre",
            summary="ancien résumé",
            content="ancien contenu",
            category=old_category,
            expires_on=datetime.date(2030, 1, 1),
        )

        proposed = {
            "title": "nouveau titre",
            "subtitle": "nouveau sous-titre",
            "summary": "nouveau résumé",
            "content": "nouveau contenu",
            "category": new_category.id,
            "expires_on": "2031-06-15",
            "as_patch": True,
        }

        url = reverse("resources-detail", args=[resource.pk])
        api_client.force_authenticate(user=user)
        response = api_client.patch(url, data=proposed)

        assert response.status_code == 201

        # a pending modification proposal has been recorded
        meta = models.ResourceRevisionMeta.objects.get(pk=response.data["id"])
        assert meta.resource == resource
        assert meta.proposed_by == user
        assert meta.kind == models.ResourceRevisionMeta.MODIFICATION
        assert meta.status == models.ResourceRevisionMeta.PENDING

        # the revision stores the proposed values
        pending_version = (
            Version.objects.get_for_object(resource)
            .filter(revision=meta.revision)
            .first()
        )
        field_dict = pending_version.field_dict
        assert field_dict["title"] == "nouveau titre"
        assert field_dict["subtitle"] == "nouveau sous-titre"
        assert field_dict["summary"] == "nouveau résumé"
        assert field_dict["content"] == "nouveau contenu"
        assert field_dict["category_id"] == new_category.id
        assert field_dict["expires_on"] == datetime.date(2031, 6, 15)

        # the live resource is left with its original values
        resource.refresh_from_db()
        assert resource.title == "ancien titre"
        assert resource.subtitle == "ancien sous-titre"
        assert resource.summary == "ancien résumé"
        assert resource.content == "ancien contenu"
        assert resource.category == old_category
        assert resource.expires_on == datetime.date(2030, 1, 1)

    @pytest.mark.django_db
    def test_creation_proposal_creates_draft_resource_and_revision(
        self, request, api_client
    ):
        """A creation proposal (POST with as_patch) creates a DRAFT resource with
        the proposed values and a pending CREATION revision awaiting moderation.

        Proposing a creation only requires being authenticated (no manage_resources).
        """
        site = get_current_site(request)

        user = baker.make(auth_models.User)
        user.profile.sites.add(site)

        category = baker.make(models.Category, sites=[site])

        proposed = {
            "title": "nouvelle ressource",
            "subtitle": "nouveau sous-titre",
            "summary": "nouveau résumé",
            "content": "nouveau contenu",
            "category": category.id,
            "expires_on": "2031-06-15",
            "status": models.Resource.PUBLISHED,
            "tags": ["un tag"],
            "as_patch": True,
        }

        url = reverse("resources-list")
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data=proposed)

        assert response.status_code == 201

        # a pending creation proposal has been recorded
        meta = models.ResourceRevisionMeta.objects.get(pk=response.data["id"])
        assert meta.revision_id == response.data["revision_id"]
        assert meta.resource_id == response.data["resource_id"]
        assert meta.proposed_by == user
        assert meta.kind == models.ResourceRevisionMeta.CREATION
        assert meta.status == models.ResourceRevisionMeta.PENDING

        # the resource is created as a DRAFT holding the proposed values
        resource = meta.resource
        assert resource.status == models.Resource.DRAFT
        assert resource.created_by == user
        assert site in resource.sites.all()
        assert resource.title == "nouvelle ressource"
        assert resource.subtitle == "nouveau sous-titre"
        assert resource.summary == "nouveau résumé"
        assert resource.content == "nouveau contenu"
        assert resource.category == category
        assert resource.expires_on == datetime.date(2031, 6, 15)

        # the revision holds the same proposed values
        version = (
            Version.objects.get_for_object(resource)
            .filter(revision=meta.revision)
            .first()
        )
        field_dict = version.field_dict
        assert field_dict["title"] == "nouvelle ressource"
        assert field_dict["content"] == "nouveau contenu"
        assert field_dict["category_id"] == category.id
        assert field_dict["expires_on"] == datetime.date(2031, 6, 15)

    # Fields the patch endpoint is allowed to modify.
    ALLOWED_PATCH_FIELDS = {
        "title",
        "subtitle",
        "summary",
        "content",
        "category",
        "expires_on",
        "contacts",
        "departments",
    }
    # Consumed by the viewset, not a resource field.
    CONTROL_FIELDS = {"as_patch"}

    @pytest.mark.django_db
    def test_patch_proposal_only_applies_whitelisted_fields(self, request, api_client):
        """Whitelisted fields land in the revision, non-whitelisted writable fields
        are ignored (revision and live resource left untouched for those)."""
        site = get_current_site(request)

        user = baker.make(auth_models.User)
        user.profile.sites.add(site)

        new_category = baker.make(models.Category, sites=[site])
        contact = baker.make("addressbook.Contact")
        department = baker.make("geomatics.Department")

        resource = baker.make(
            models.Resource,
            sites=[site],
            site_origin=site,
            status=models.Resource.PUBLISHED,
            support_orga="structure officielle",
            title="ancien titre",
            content="ancien contenu",
        )
        resource.tags.set(["tag-officiel"])
        resource.refresh_from_db()

        # writable serializer fields split between allowed and forbidden ones
        serializer_fields = ResourceWritableSerializer().fields
        writable_fields = {
            name for name, field in serializer_fields.items() if not field.read_only
        }
        forbidden_fields = (
            writable_fields - self.ALLOWED_PATCH_FIELDS - self.CONTROL_FIELDS
        )
        assert forbidden_fields, "expected some writable fields to be protected"

        # new values sent for every whitelisted field, expected back in the revision
        allowed_values = {
            "title": "nouveau titre",
            "subtitle": "nouveau sous-titre",
            "summary": "nouveau résumé",
            "content": "nouveau contenu",
            "category": new_category,
            "expires_on": datetime.date(2031, 6, 15),
            "contacts": [contact],
            "departments": [department],
        }
        assert set(allowed_values) == self.ALLOWED_PATCH_FIELDS

        # distinct value we try to smuggle in for each forbidden field
        poison_values = {
            "status": models.Resource.TO_REVIEW,
            "support_orga": "structure pirate",
            "tags": ["tag-pirate"],
            "created_on": "2000-01-01T00:00:00Z",
            "updated_on": "2000-01-01T00:00:00Z",
            "nb_uses": 9999,
        }
        # fail if the serializer exposes a new forbidden field we don't exercise
        assert forbidden_fields <= set(poison_values), (
            f"unhandled forbidden fields: {forbidden_fields - set(poison_values)}"
        )

        def live_value(field):
            """Current value of a forbidden field on the live resource."""
            if field == "tags":
                return sorted(resource.tags.names())
            if field == "nb_uses":  # annotation, not persisted
                return None
            return getattr(resource, field)

        original = {field: live_value(field) for field in forbidden_fields}

        def to_payload(field, value):
            if field == "category":
                return value.pk
            if field in ("contacts", "departments"):
                return [obj.pk for obj in value]
            if field == "expires_on":
                return value.isoformat()
            return value

        payload = {"as_patch": True}
        for field, value in allowed_values.items():
            payload[field] = to_payload(field, value)
        for field in forbidden_fields:
            payload[field] = poison_values[field]

        url = reverse("resources-detail", args=[resource.pk])
        api_client.force_authenticate(user=user)
        response = api_client.patch(url, data=payload, format="json")

        assert response.status_code == 201

        meta = models.ResourceRevisionMeta.objects.get(pk=response.data["id"])
        field_dict = (
            Version.objects.get_for_object(resource)
            .filter(revision=meta.revision)
            .first()
            .field_dict
        )

        # every whitelisted field made it into the revision
        for field, value in allowed_values.items():
            if field == "category":
                assert field_dict["category_id"] == value.pk
            elif field in ("contacts", "departments"):
                assert set(field_dict[field]) == {obj.pk for obj in value}
            else:
                assert field_dict[field] == value

        # every forbidden field is untouched, in the revision and on the live resource
        resource.refresh_from_db()
        for field in forbidden_fields:
            assert live_value(field) == original[field]
            if field in field_dict:
                assert field_dict[field] == original[field]


class TestRessourceAddonViewSet:
    @pytest.mark.django_db
    def test_not_authenticated(self, api_client):
        response = api_client.get(reverse("resource-addons-list"))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_not_authorized(self, api_client):
        user = baker.make(auth_models.User)
        api_client.force_authenticate(user)
        response = api_client.get(reverse("resource-addons-list"))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_list_resource_addons(self, api_client, current_site):
        user = baker.make(auth_models.User)
        assign_perm("sites.manage_resources", user, current_site)

        resource_addon = baker.make(
            models.ResourceAddon,
            nature="hub_with_iframe",
            recommendation__site=current_site,
            data={
                "title": "Hub avec iframe",
                "iframe_url": "https://www.example.com",
            },
            enabled=True,
        )

        api_client.force_authenticate(user)
        response = api_client.get(reverse("resource-addons-list"))
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0] == {
            "id": resource_addon.id,
            "nature": "hub_with_iframe",
            "recommendation": resource_addon.recommendation_id,
            "data": {
                "title": "Hub avec iframe",
                "iframe_url": "https://www.example.com",
            },
            "enabled": True,
        }

    @pytest.mark.django_db
    def test_create_resource_addon(self, api_client, current_site):
        user = baker.make(auth_models.User)
        assign_perm("sites.manage_resources", user, current_site)

        resource = baker.make("resources.Resource", sites=[current_site])
        recommendation = baker.make("tasks.Task", site=current_site, resource=resource)

        api_client.force_authenticate(user)
        response = api_client.post(
            reverse("resource-addons-list"),
            data={
                "nature": "hub_with_iframe",
                "recommendation": recommendation.id,
                "data": json.dumps(
                    {
                        "title": "Hub avec iframe",
                        "iframe_url": "https://www.example.com",
                    }
                ),
                "enabled": True,
            },
        )
        assert response.status_code == 201

        recommendation.refresh_from_db()

        assert recommendation.resource_addons.count() == 1
        addon = recommendation.resource_addons.first()
        assert addon.nature == "hub_with_iframe"
        assert addon.recommendation == recommendation
        assert addon.data == {
            "title": "Hub avec iframe",
            "iframe_url": "https://www.example.com",
        }
        assert addon.enabled is True
