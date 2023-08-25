from django.contrib.auth import models as auth_models
from urbanvitaliz import utils
from urbanvitaliz.apps.communication import api as communication_api
from urbanvitaliz.apps.communication import digests

from . import models


def invite_collaborator_on_project(site, project, role, email, message, inviter):
    """Invite a collaborator using her email on a given project"""
    if role not in [e[0] for e in models.Invite.INVITE_ROLES]:
        return None

    if project is None:
        return None

    # Try to resolve email to a user first
    try:
        user = auth_models.User.objects.get(username=email)
    except auth_models.User.DoesNotExist:
        user = None

    already_invited = models.Invite.on_site.filter(
        project=project, site=site, email=email, accepted_on=None
    ).exists()

    already_member = False

    if user and user in project.members.all():
        already_member = True

    # Already invited, skip
    if already_member or already_invited:
        return False

    invite = models.Invite.objects.create(
        project=project,
        email=email,
        role=role,
        message=message,
        inviter=inviter,
        site=site,
    )

    invite_send(invite, invited_user=user)

    return invite


def invite_send(invite, invited_user=None):
    # Dispatch notifications
    params = {
        "sender": {
            "first_name": invite.inviter.first_name,
            "last_name": invite.inviter.last_name,
            "email": invite.inviter.email,
        },
        "message": invite.message,
        "invite_url": utils.build_absolute_url(
            invite.get_absolute_url(), auto_login_user=invited_user
        ),
        "project": digests.make_project_digest(invite.project),
    }

    if invite.inviter.profile:
        if invite.inviter.profile.organization:
            params["sender"]["organization"] = invite.inviter.profile.organization.name

    res = communication_api.send_email(
        template_name="sharing invitation",
        recipients=[{"email": invite.email}],
        params=params,
    )

    return bool(res)


def invite_resend(invite):
    """Resend the invitation email"""
    try:
        user = auth_models.User.objects.get(username=invite.email)
    except auth_models.User.DoesNotExist:
        user = None  # Used to generate autologging link

    return invite_send(invite, invited_user=user)


def invite_revoke(invite):
    """Revoke an invitation"""
    if invite.accepted_on is None:
        invite.delete()
        return True

    return False


# eof
