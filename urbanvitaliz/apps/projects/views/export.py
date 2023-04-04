# encoding: utf-8

"""
Export views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2023-01-10 17:20:20 CEST
"""

import csv
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from urbanvitaliz.apps.crm import models as crm_models
from urbanvitaliz.apps.reminders import models as reminders_models
from urbanvitaliz.utils import build_absolute_url, is_switchtender_or_403

from .. import models
from ..utils import (format_switchtender_identity,
                     get_collaborators_for_project,
                     get_switchtenders_for_project)


@login_required
@ensure_csrf_cookie
def project_list_export_csv(request):
    """Export the projects for the switchtender as CSV"""
    is_switchtender_or_403(request.user)

    projects = (
        models.Project.on_site.for_user(request.user)
        .exclude(status="DRAFT")
        .order_by("-created_on")
    )

    project_ct = ContentType.objects.get_for_model(models.Project)

    today = datetime.datetime.today().date()

    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="urbanvitaliz-projects-{today}.csv"'
        },
    )

    writer = csv.writer(response, quoting=csv.QUOTE_ALL)
    writer.writerow(
        [
            "departement",
            "commune_insee",
            "nom_friche",
            "detail_adresse",
            "date_contact",
            "contact_dossier",
            "mail",
            "tel",
            "conseillers",
            "statut_conseil",
            "nb_reco",
            "nb_reco_nonstaff",
            "nb_reco_actives",
            "nb_interactions_reco",
            "nb_commentaires_recos",
            "nb_commentaires_recos_nonstaff",
            "nb_rappels",
            "nb_messages_conversation_conseillers_nonstaff",
            "nb_messages_conversation_collectivite",
            "nb_messages_suivis_int_nonstaff",
            "nb_conseillers_nonstaff",
            "tags",
            "lien_projet",
            "exclude_stats",
            "impact_edl",
            "impact_diag",
            "impact_mise_en_relation",
        ]
    )

    for project in projects:
        switchtenders = get_switchtenders_for_project(project)
        switchtenders_txt = ", ".join(
            [format_switchtender_identity(u) for u in switchtenders]
        )

        collaborators = get_collaborators_for_project(project)

        followups = models.TaskFollowup.objects.filter(
            task__project=project,
            task__site=request.site,
        )

        notes = models.Note.objects.filter(
            project=project,
            created_by__in=switchtenders,
            created_by__is_staff=False,
        )

        crm_notes = crm_models.Note.objects.filter(
            content_type_id=project_ct.pk, object_id=project.pk
        )

        conversations = models.Note.objects.filter(project=project).filter(public=True)

        published_tasks = project.tasks.filter(site=request.site).exclude(public=False)

        writer.writerow(
            [
                project.commune.department.code if project.commune else "??",
                project.commune.insee if project.commune else "??",
                project.name,
                project.location,
                project.created_on.date(),
                f"{project.first_name} {project.last_name}",
                [m.email for m in project.members.all()],
                project.phone,
                switchtenders_txt,
                project.status,
                published_tasks.count(),
                published_tasks.exclude(created_by__is_staff=True).count(),
                published_tasks.filter(
                    status__in=(
                        models.Task.INPROGRESS,
                        models.Task.BLOCKED,
                        models.Task.DONE,
                    )
                ).count(),
                followups.exclude(status=None).exclude(who__in=switchtenders).count(),
                followups.exclude(comment="").exclude(who__in=switchtenders).count(),
                (
                    followups.exclude(comment="")
                    .filter(who__in=switchtenders, who__is_staff=False)
                    .count()
                ),
                reminders_models.Reminder.objects.filter(
                    tasks__site=request.site,
                    tasks__project=project,
                    origin=reminders_models.Reminder.SELF,
                ).count(),  # Reminders
                notes.filter(public=True).count(),  # conversations conseillers
                max(
                    0, conversations.filter(created_by__in=collaborators).count() - 1
                ),  # conversations collectivite. -1 to remove a message from the system
                notes.filter(public=False).count(),  # suivi interne conseillers
                switchtenders.exclude(
                    groups=["example_com_staff"]
                ).count(),  # non staff switchtender count
                [tag for tag in project.tags.names()],
                build_absolute_url(
                    reverse("projects-project-detail", args=[project.id])
                ),
                project.exclude_stats,
                crm_notes.filter(tags__name__in=["impact edl"]).count(),
                crm_notes.filter(tags__name__in=["impact diag"]).count(),
                crm_notes.filter(tags__name__in=["impact mise en relation"]).count(),
            ]
        )

    return response
