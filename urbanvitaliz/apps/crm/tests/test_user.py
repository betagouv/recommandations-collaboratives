import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from pytest_django.asserts import assertContains, assertNotContains

from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import get_group_for_site, login

########################################################################
# users list
########################################################################


@pytest.mark.django_db
def test_crm_user_list_not_available_for_non_staff(client):
    url = reverse("crm-user-list")
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_user_list_contains_site_users(request, client):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)

    advisor = baker.make(auth_models.User)
    advisor.profile.sites.add(site)
    gadvisor = auth_models.Group.objects.get(name="example_com_advisor")
    advisor.groups.add(gadvisor)

    a_user = baker.make(auth_models.User)
    a_user.profile.sites.add(site)

    other = baker.make(auth_models.User)

    url = reverse("crm-user-list")

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200

    for user in [staff, advisor, a_user]:
        expected = reverse("crm-user-details", args=[user.id])
        assertContains(response, expected)

    unexpected = reverse("crm-user-details", args=[other.id])
    assertNotContains(response, unexpected)


@pytest.mark.django_db
def test_crm_user_list_filters_only_selected_user(request, client):
    site = get_current_site(request)

    expected = baker.make(auth_models.User)
    expected.profile.sites.add(site)

    unexpected = baker.make(auth_models.User)
    unexpected.profile.sites.add(site)

    url = reverse("crm-user-list") + f"?username={expected.username}"

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-user-details", args=[expected.id])
    assertContains(response, expected)

    unexpected = reverse("crm-user-details", args=[unexpected.id])
    assertNotContains(response, unexpected)


@pytest.mark.django_db
def test_crm_user_list_filters_only_user_matching_partial(request, client):
    site = get_current_site(request)

    expected = baker.make(auth_models.User, username="doe@example.com")
    expected.profile.sites.add(site)

    unexpected = baker.make(auth_models.User, username="smith@example.com")
    unexpected.profile.sites.add(site)

    url = reverse("crm-user-list") + "?username=doe"

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-user-details", args=[expected.id])
    assertContains(response, expected)

    unexpected = reverse("crm-user-details", args=[unexpected.id])
    assertNotContains(response, unexpected)


@pytest.mark.django_db
def test_crm_user_list_filters_only_inactive_user(request, client):
    site = get_current_site(request)

    active = baker.make(auth_models.User, is_active=True)
    active.profile.sites.add(site)

    inactive = baker.make(auth_models.User, is_active=False)
    inactive.profile.sites.add(site)

    url = reverse("crm-user-list") + "?inactive=true"

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-user-details", args=[inactive.id])
    assertContains(response, expected)

    unexpected = reverse("crm-user-details", args=[active.id])
    assertNotContains(response, unexpected)


@pytest.mark.django_db
def test_crm_user_list_filters_only_selected_role(request, client):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)

    advisor = baker.make(auth_models.User)
    advisor.profile.sites.add(site)
    gadvisor = auth_models.Group.objects.get(name="example_com_advisor")
    advisor.groups.add(gadvisor)

    a_user = baker.make(auth_models.User)
    a_user.profile.sites.add(site)

    url = reverse("crm-user-list") + "?role=2"  # role 2 is staff

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-user-details", args=[staff.id])
    assertContains(response, expected)

    unexpected = reverse("crm-user-details", args=[advisor.id])
    assertNotContains(response, unexpected)

    unexpected = reverse("crm-user-details", args=[a_user.id])
    assertNotContains(response, unexpected)


########################################################################
# details
########################################################################


@pytest.mark.django_db
def test_crm_user_details_available_for_staff(client):
    user = baker.make(auth_models.User)

    url = reverse("crm-user-details", args=[user.pk])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


########################################################################
# update user / profile information
########################################################################


@pytest.mark.django_db
def test_crm_user_update_not_available_for_non_staff(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User)
    user.profile.sites.add(site)

    url = reverse("crm-user-update", args=[user.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_user_update_available_for_staff(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User)

    url = reverse("crm-user-update", args=[user.id])
    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_user_update_profile_information(request, client):
    site = get_current_site(request)

    organization = baker.make(addressbook_models.Organization)

    end_user = baker.make(auth_models.User)
    profile = end_user.profile

    url = reverse("crm-user-update", args=[end_user.id])
    data = {
        "first_name": "John",
        "last_name": "DOE",
        "phone_no": "01 23 45 67 89",
        "organization": organization.id,
        "organization_position": "staff",
    }

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.post(url, data=data)

    assert response.status_code == 302

    # user data is updated
    end_user.refresh_from_db()

    assert end_user.first_name == data["first_name"]
    assert end_user.last_name == data["last_name"]

    # profile is updated
    profile.refresh_from_db()

    assert profile.phone_no == data["phone_no"]
    assert profile.organization == organization
    assert profile.organization_position == data["organization_position"]


########################################################################
# user deactivation
########################################################################


@pytest.mark.django_db
def test_crm_user_deactivate_page_requires_permission(request, client):
    end_user = baker.make(auth_models.User, is_active=False)

    url = reverse("crm-user-deactivate", args=[end_user.id])

    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_user_deactivate_page_with_permission(request, client):
    site = get_current_site(request)

    end_user = baker.make(auth_models.User, is_active=False)

    url = reverse("crm-user-deactivate", args=[end_user.id])

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_user_deactivate_processing(request, client):
    site = get_current_site(request)

    end_user = baker.make(auth_models.User, is_active=True)

    url = reverse("crm-user-deactivate", args=[end_user.id])

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.post(url)

    assert response.status_code == 302

    # user data is updated
    end_user.refresh_from_db()
    assert end_user.is_active is False
    assert end_user.profile.deleted is not None


########################################################################
# user reactivation
########################################################################


@pytest.mark.django_db
def test_crm_user_reactivate_page_requires_permission(request, client):
    end_user = baker.make(auth_models.User, is_active=False)

    url = reverse("crm-user-reactivate", args=[end_user.id])

    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_user_reactivate_page_with_permission(request, client):
    site = get_current_site(request)

    end_user = baker.make(auth_models.User, is_active=False)

    url = reverse("crm-user-reactivate", args=[end_user.id])

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_user_reactivate_processing(request, client):
    site = get_current_site(request)

    end_user = baker.make(auth_models.User, is_active=False)

    url = reverse("crm-user-reactivate", args=[end_user.id])

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.post(url)

    assert response.status_code == 302

    # user data is updated
    end_user.refresh_from_db()
    assert end_user.is_active is True
    assert end_user.profile.deleted is None


########################################################################
# user set advisor status
########################################################################


@pytest.mark.django_db
def test_crm_user_set_advisor_page_requires_permission(request, client):
    end_user = baker.make(auth_models.User, is_active=False)

    url = reverse("crm-user-set-advisor", args=[end_user.id])

    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_user_set_advisor_page_with_permission(request, client):
    site = get_current_site(request)

    end_user = baker.make(auth_models.User, is_active=False)

    url = reverse("crm-user-set-advisor", args=[end_user.id])

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_user_set_advisor_processing(request, client):
    site = get_current_site(request)

    departments = baker.make(geomatics.Department, _quantity=4)

    end_user = baker.make(auth_models.User)

    url = reverse("crm-user-set-advisor", args=[end_user.id])

    selected = [d.code for d in departments[1:3]]
    data = {"departments": selected}

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.post(url, data=data)

    assert response.status_code == 302

    # user data is updated
    end_user.refresh_from_db()

    group = get_group_for_site("advisor", site)
    assert group in end_user.groups.all()

    user_dpts = (d.code for d in end_user.profile.departments.all())
    assert set(user_dpts) == set(selected)


########################################################################
# user unset advisor status
########################################################################


@pytest.mark.django_db
def test_crm_user_unset_advisor_page_requires_permission(request, client):
    end_user = baker.make(auth_models.User, is_active=False)

    url = reverse("crm-user-unset-advisor", args=[end_user.id])

    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_user_unset_advisor_page_with_permission(request, client):
    site = get_current_site(request)

    end_user = baker.make(auth_models.User, is_active=False)

    url = reverse("crm-user-unset-advisor", args=[end_user.id])

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_user_unset_advisor_processing(request, client):
    site = get_current_site(request)

    departments = baker.make(geomatics.Department, _quantity=2)

    end_user = baker.make(auth_models.User)
    end_user.profile.departments.set(departments)
    group = get_group_for_site("advisor", site)
    end_user.groups.add(group)

    url = reverse("crm-user-unset-advisor", args=[end_user.id])

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.post(url)

    assert response.status_code == 302

    # user data is updated
    end_user.refresh_from_db()

    assert end_user.groups.count() == 0

    assert end_user.profile.departments.count() == 0


########################################################################
# user project interest
########################################################################


@pytest.mark.django_db
def test_crm_user_project_interest_not_accessible_wo_perm(request, client):
    site = get_current_site(request)
    o = baker.make(auth_models.User)
    o.profile.sites.add(site)

    url = reverse("crm-user-project-interest", args=[o.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_user_project_interest_not_accessible_other_site(request, client):
    site = get_current_site(request)
    other = baker.make(site_models.Site)
    o = baker.make(auth_models.User)
    o.profile.sites.add(other)

    url = reverse("crm-user-project-interest", args=[o.id])
    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_user_project_interest_accessible_w_perm(request, client):
    site = get_current_site(request)
    other = baker.make(site_models.Site)

    o = baker.make(auth_models.User)
    o.profile.sites.add(site)

    expected = baker.make(projects_models.UserProjectStatus, site=site, user=o)
    other_site = baker.make(projects_models.UserProjectStatus, site=other, user=o)
    unexpected = baker.make(projects_models.UserProjectStatus, site=site)

    url = reverse("crm-user-project-interest", args=[o.id])
    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200

    assertContains(response, expected.project.name[:10])
    assertNotContains(response, unexpected.project.name)
    assertNotContains(response, other_site.project.name)


########################################################################
# user notifications
########################################################################


@pytest.mark.django_db
def test_crm_user_notification_not_accessible_wo_perm(request, client):
    site = get_current_site(request)

    o = baker.make(auth_models.User)
    o.profile.sites.add(site)

    url = reverse("crm-user-notifications", args=[o.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_user_notification_not_accessible_other_site(request, client):
    site = get_current_site(request)
    other = baker.make(site_models.Site)
    o = baker.make(auth_models.User)
    o.profile.sites.add(other)

    url = reverse("crm-user-notifications", args=[o.id])
    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_user_notification_accessible_w_perm(request, client):
    site = get_current_site(request)
    # other = baker.make(site_models.Site)

    o = baker.make(auth_models.User)
    o.profile.sites.add(site)

    # on_site = baker.make(
    #     notifications_models.Notification, site=site, recipient=o, emailed=True
    # )
    # other_site = baker.make(
    #     notifications_models.Notification, site=other, recipient=o, emailed=True
    # )
    # other_user = baker.make(
    #     notifications_models.Notification, site=site, emailed=True
    # )

    url = reverse("crm-user-notifications", args=[o.id])
    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200

    # assertContains(response, on_site.verb[:16])
    # assertNotContains(response, other_site.verb[:16])
    # assertNotContains(response, other_user.verb[:16])


# eof
