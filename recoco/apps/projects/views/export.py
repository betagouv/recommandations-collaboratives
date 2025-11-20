# encoding: utf-8

"""
Export views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2023-01-10 17:20:20 CEST
"""

import csv
import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from recoco.apps.crm import models as crm_models
from recoco.apps.tasks import models as task_models
from recoco.utils import build_absolute_url, get_group_for_site, is_switchtender_or_403

from .. import models
from ..utils import (
    format_switchtender_identity,
    get_collaborators_for_project,
    get_switchtenders_for_project,
)


@login_required
@ensure_csrf_cookie
def project_list_export_csv(request):
    """Export the projects for the switchtender as CSV"""
    is_switchtender_or_403(request.user)

    projects = (
        models.Project.on_site.for_user(request.user)
        .exclude(project_sites__status="DRAFT")
        .order_by("-created_on")
        .prefetch_related("notes", "tasks")
    )

    today = datetime.datetime.today().date()

    content_disposition = f'attachment; filename="projects-{today}.csv"'
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": content_disposition},
    )

    writer = csv.writer(response, quoting=csv.QUOTE_ALL)

    columns = [
        "departement",
        "commune_insee",
        "commune_nom",
        "nom_dossier",
        "detail_adresse",
        "date_contact",
        "contact_dossier",
        "mail",
        "tel",
        "conseillers",
        "statut_conseil",
        "premiere_reco_le",
        "nb_reco",
        "nb_reco_nonstaff",
        "nb_reco_actives",
        "nb_interactions_reco",
        "nb_commentaires_recos",
        "nb_commentaires_recos_nonstaff",
        # "nb_rappels",
        "nb_messages_conversation_conseillers_nonstaff",
        "nb_messages_conversation_collectivite",
        "nb_messages_suivis_int_nonstaff",
        "nb_conseillers_nonstaff",
        "tags",
        "lien_dossier",
        "exclude_stats",
        "origin_site",
    ]

    site_config = request.site_config

    tags_for_site = [tag.name for tag in site_config.crm_available_tags.all()]
    for tag in tags_for_site:
        columns.append(tag)

    writer.writerow(columns)

    staff_group = get_group_for_site("staff", request.site)

    for project in projects:
        switchtenders = get_switchtenders_for_project(project)
        switchtenders_txt = ", ".join(
            [format_switchtender_identity(u) for u in switchtenders]
        )

        collaborators = get_collaborators_for_project(project)

        followups = task_models.TaskFollowup.objects.filter(
            task__project=project,
            task__site=request.site,
        )

        private_conversations = project.notes.filter(
            created_by__in=switchtenders,
            created_by__is_staff=False,
        )

        conversations = project.public_messages.filter(deleted=None)

        published_tasks = project.tasks.filter(site=request.site).exclude(public=False)
        first_reco = published_tasks.order_by("created_on").first()

        row = [
            project.commune.department.code if project.commune else "??",
            project.commune.insee if project.commune else "??",
            project.commune.name if project.commune else "??",
            project.name,
            project.location,
            project.created_on.date(),
            f"{project.first_name} {project.last_name}",
            [m.email for m in project.members.all()],
            project.phone,
            switchtenders_txt,
            project.project_sites.current().status,
            first_reco.created_on.date() if first_reco else "",  # First reco date
            published_tasks.exclude(status=task_models.Task.NOT_INTERESTED).count(),
            published_tasks.exclude(status=task_models.Task.NOT_INTERESTED)
            .exclude(created_by__is_staff=True)
            .count(),
            published_tasks.filter(
                status__in=(
                    task_models.Task.INPROGRESS,
                    task_models.Task.BLOCKED,
                    task_models.Task.DONE,
                )
            ).count(),
            followups.exclude(status=None)
            .exclude(task__status=task_models.Task.NOT_INTERESTED)
            .exclude(who__in=switchtenders)
            .count(),
            followups.exclude(task__status=task_models.Task.NOT_INTERESTED)
            .exclude(comment="")
            .exclude(who__in=switchtenders)
            .count(),
            (
                followups.exclude(comment="")
                .filter(who__in=switchtenders, who__is_staff=False)
                .count()
            ),
            # reminders_models.Reminder.objects.filter(
            #     tasks__site=request.site,
            #     tasks__project=project,
            #     origin=reminders_models.Reminder.SELF,
            # ).count(),  # Reminders
            conversations.filter(
                posted_by__in=switchtenders, posted_by__is_staff=False
            ).count(),  # conversations conseillers
            conversations.filter(
                posted_by__in=collaborators
            ).count(),  # conversations project members
            private_conversations.filter(
                public=False
            ).count(),  # suivi interne conseillers
            switchtenders.exclude(
                groups__in=[staff_group]
            ).count(),  # non staff switchtender count
            [tag for tag in project.tags.names()],
            build_absolute_url(reverse("projects-project-detail", args=[project.id])),
            project.exclude_stats,
            project.project_sites.origin().site.domain,
        ]

        try:
            annotation = crm_models.ProjectAnnotations.objects.get(
                project=project, site=request.site
            )
            for tag in tags_for_site:
                row.append(1 if tag in annotation.tags.names() else 0)
        except crm_models.ProjectAnnotations.DoesNotExist:
            for _ in tags_for_site:
                row.append(0)

        writer.writerow(row)

    return response
