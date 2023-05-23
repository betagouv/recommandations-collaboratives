# encoding: utf-8

"""
Urls for crm application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-07-19 17:27:25 CEST
"""


from django.urls import path

from . import views

urlpatterns = [
    path(
        r"crm/",
        views.CRMSiteDashboardView.as_view(),
        name="crm-site-dashboard",
    ),
    path(
        r"crm/search",
        views.crm_search,
        name="crm-search",
    ),
    path(
        r"crm/tags",
        views.crm_list_tags,
        name="crm-list-tags",
    ),
    path(
        r"crm/org/<int:organization_id>/",
        views.organization_details,
        name="crm-organization-details",
    ),
    #
    # users
    path(
        r"crm/users/",
        views.user_list,
        name="crm-user-list",
    ),
    path(
        r"crm/user/<int:user_id>/",
        views.user_details,
        name="crm-user-details",
    ),
    path(
        r"crm/user/<int:user_id>/update/",
        views.user_update,
        name="crm-user-update",
    ),
    path(
        r"crm/user/<int:user_id>/advisor/set/",
        views.user_set_advisor,
        name="crm-user-set-advisor",
    ),
    path(
        r"crm/user/<int:user_id>/advisor/unset/",
        views.user_unset_advisor,
        name="crm-user-unset-advisor",
    ),
    path(
        r"crm/user/<int:user_id>/deactivate/",
        views.user_deactivate,
        name="crm-user-deactivate",
    ),
    path(
        r"crm/user/<int:user_id>/reactivate/",
        views.user_reactivate,
        name="crm-user-reactivate",
    ),
    path(
        r"crm/user/<int:user_id>/project_interest",
        views.user_project_interest,
        name="crm-user-project-interest",
    ),
    path(
        r"crm/user/<int:user_id>/notifications",
        views.user_notifications,
        name="crm-user-notifications",
    ),
    #
    # projects
    path(
        r"crm/project/",
        views.project_list,
        name="crm-project-list",
    ),
    path(
        r"crm/project/<int:project_id>/",
        views.project_details,
        name="crm-project-details",
    ),
    path(
        r"crm/project/<int:project_id>/update/",
        views.project_update,
        name="crm-project-update",
    ),
    path(
        r"crm/project/<int:project_id>/delete/",
        views.project_delete,
        name="crm-project-delete",
    ),
    path(
        r"crm/project/<int:project_id>/undelete/",
        views.project_undelete,
        name="crm-project-undelete",
    ),
    path(
        r"crm/project/<int:project_id>/annotation/toggle/",
        views.project_toggle_annotation,
        name="crm-project-toggle-annotation",
    ),
    #
    # Organization
    path(
        r"crm/org/",
        views.organization_list,
        name="crm-organization-list",
    ),
    path(
        r"crm/org/<int:organization_id>/update/",
        views.organization_update,
        name="crm-organization-update",
    ),
    path(
        r"crm/org/<int:organization_id>/merge/",
        views.organization_merge,
        name="crm-organization-merge",
    ),
    path(
        r"crm/org/<int:organization_id>/create-note",
        views.create_note_for_organization,
        name="crm-organization-note-create",
    ),
    path(
        r"crm/org/<int:organization_id>/note/<int:note_id>",
        views.update_note_for_organization,
        name="crm-organization-note-update",
    ),
    path(
        r"crm/user/<int:user_id>/create-note",
        views.create_note_for_user,
        name="crm-user-note-create",
    ),
    path(
        r"crm/user/<int:user_id>/note/<int:note_id>",
        views.update_note_for_user,
        name="crm-user-note-update",
    ),
    path(
        r"crm/project/<int:project_id>/create-note",
        views.create_note_for_project,
        name="crm-project-note-create",
    ),
    path(
        r"crm/project/<int:project_id>/note/<int:note_id>",
        views.update_note_for_project,
        name="crm-project-note-update",
    ),
    path(
        r"crm/projects/by_tags",
        views.project_list_by_tags,
        name="crm-project-list-by-tags",
    ),
    path(
        r"crm/projects/by_tags.csv",
        views.project_list_by_tags_as_csv,
        name="crm-project-list-by-tags-csv",
    ),
    path("crm/feed/", views.LatestNotesFeed(), name="crm-feed"),
]
