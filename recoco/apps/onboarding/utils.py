# encoding: utf-8

"""
views for onboarding new users/projects

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-07-17 20:39:35 CEST
"""

from django.contrib import messages
from django.contrib.auth import models as auth
from django.contrib.sites import models as sites

from recoco.apps.communication import constants as communication_constants
from recoco.apps.communication import digests
from recoco.apps.communication.api import send_email
from recoco.apps.communication.digests import normalize_user_name
from recoco.apps.invites import models as invites
from recoco.apps.projects import models as projects
from recoco.apps.projects import signals as projects_signals
from recoco.utils import build_absolute_url


def notify_new_project(
    site: sites.Site, project: projects.Project, owner: auth.User
) -> None:
    """Create notification of new project"""

    # notify project submission
    projects_signals.project_submitted.send(
        sender=projects.Project,
        site=site,
        submitter=owner,
        project=project,
    )


def email_owner_of_project(
    site: sites.Site, project: projects.Project, user: auth.User
) -> None:
    """Send email to new project owner"""

    # Send an email to the project owner
    params = {
        "project": digests.make_project_digest(
            project, project.owner, url_name="knowledge"
        ),
    }
    send_email(
        template_name=communication_constants.TPL_PROJECT_RECEIVED,
        recipients=[
            {
                "name": normalize_user_name(project.owner),
                "email": project.owner.email,
            }
        ],
        params=params,
    )
    # FIXME return send_mail status ?


def invite_user_to_project(
    request, user: auth.User, project: projects.Project, is_new_user: bool
):
    invite, _ = invites.Invite.objects.get_or_create(
        project=project,
        inviter=request.user,
        site=request.site,
        email=user.email,
        defaults={
            "message": (
                "Je viens de déposer votre dossier sur la"
                "plateforme de manière à faciliter nos échanges."
            )
        },
    )

    send_email(
        template_name=communication_constants.TPL_SHARING_INVITATION,
        recipients=[{"email": user.email}],
        params={
            "sender": {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
            },
            "message": invite.message,
            "invite_url": build_absolute_url(
                invite.get_absolute_url(),
                auto_login_user=user,
            ),
            "project": digests.make_project_digest(project),
        },
    )

    messages.success(
        request,
        (
            "Un courriel d'invitation à rejoindre"
            f" le dossier a été envoyé à {user.email}."
        ),
        extra_tags=["email"],
    )
