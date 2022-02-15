# encoding: utf-8

"""
tests for digesting emails

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2022-02-03 16:14:54 CET
"""

from django.contrib.auth import models as auth
from model_bakery import baker
from model_bakery.recipe import Recipe
from notifications import models as notifications_models
from notifications.signals import notify
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.geomatics import models as geomatics_models
from urbanvitaliz.apps.resources import models as resources_models

from .. import digests, models, signals
from ..digests import NotificationFormatter

########################################################################
# new reco digests
########################################################################


def test_send_digests_for_new_reco(client):
    user = Recipe(auth.User, username="auser", email="user@example.com").make()
    switchtender = Recipe(
        auth.User, username="switchtender", email="switchtender@example.com"
    ).make()
    project = baker.make(models.Project, status="DONE", emails=[user.email])

    # Generate a notification
    signals.action_created.send(
        sender=test_send_digests_for_new_reco,
        task=models.Task.objects.create(project=project, created_by=switchtender),
        project=project,
        user=switchtender,
    )

    digests.send_digests_for_new_recommendations_by_user(user)

    assert user.notifications.unsent().count() == 0


def test_send_digests_for_new_reco_empty(client):
    user = Recipe(auth.User, username="auser", email="user@example.com").make()

    baker.make(models.Project, status="DONE", emails=[user.email])

    digests.send_digests_for_new_recommendations_by_user(user)

    assert user.notifications.unsent().count() == 0


def test_send_digests_for_new_reco_not_sent_for_not_done_projects(client):
    user = Recipe(auth.User, username="auser", email="user@example.com").make()
    switchtender = Recipe(
        auth.User, username="switchtender", email="switchtender@example.com"
    ).make()
    project = baker.make(models.Project, status="READY", emails=[user.email])

    # Generate a notification
    signals.action_created.send(
        sender=test_send_digests_for_new_reco,
        task=models.Task.objects.create(project=project, created_by=switchtender),
        project=project,
        user=switchtender,
    )

    digests.send_digests_for_new_recommendations_by_user(user)

    assert user.notifications.unsent().count() == 1


########################################################################
# new sites digests
########################################################################


def test_send_digests_for_new_sites_by_user():
    st_group, created = auth.Group.objects.get_or_create(name="switchtender")
    auth.Group.objects.get_or_create(name="project_moderator")

    # regional actor
    dpt_nord = Recipe(geomatics_models.Department, code=59, name="Nord").make()
    commune = Recipe(
        geomatics_models.Commune, name="Lille", postal="59000", department=dpt_nord
    ).make()
    regional_actor = Recipe(auth.User).make()
    regional_actor.groups.add(st_group)
    regional_actor.profile.departments.add(dpt_nord)

    # non regional actor
    dpt_npdc = Recipe(geomatics_models.Department, code=62, name="PDC").make()
    commune = Recipe(
        geomatics_models.Commune, name="Attin", postal="62170", department=dpt_nord
    ).make()
    non_regional_actor = Recipe(auth.User).make()
    non_regional_actor.groups.add(st_group)
    non_regional_actor.profile.departments.add(dpt_npdc)

    # moderator
    moderator = Recipe(auth.User).make()

    user = Recipe(auth.User, username="auser", email="user@example.com").make()
    project = baker.make(
        models.Project,
        email=user.email,
        emails=[user.email],
        commune=commune,
        status="READY",
    )

    # Generate a notification
    signals.project_validated.send(
        sender=models.Project, moderator=moderator, project=project
    )

    assert regional_actor.notifications.unsent().count() == 1
    assert non_regional_actor.notifications.unsent().count() == 0

    digests.send_digests_for_new_sites_by_user(regional_actor)
    digests.send_digests_for_new_sites_by_user(non_regional_actor)

    assert regional_actor.notifications.unsent().count() == 0
    assert non_regional_actor.notifications.unsent().count() == 0


def test_send_digests_for_switchtender_by_user(client):
    st_group, created = auth.Group.objects.get_or_create(name="switchtender")
    auth.Group.objects.get_or_create(name="project_moderator")

    # regional actor
    dpt_nord = Recipe(geomatics_models.Department, code=59, name="Nord").make()
    commune = Recipe(
        geomatics_models.Commune, name="Lille", postal="59000", department=dpt_nord
    ).make()

    organization = Recipe(addressbook_models.Organization, name="Orga").make()
    regional_actor = Recipe(auth.User).make()
    regional_actor.profile.organization = organization
    regional_actor.profile.save()
    regional_actor.groups.add(st_group)
    regional_actor.profile.departments.add(dpt_nord)

    regional_actor2 = Recipe(auth.User).make()
    regional_actor2.groups.add(st_group)
    regional_actor2.profile.departments.add(dpt_nord)

    # non regional actor
    dpt_npdc = Recipe(geomatics_models.Department, code=62, name="PDC").make()
    commune = Recipe(
        geomatics_models.Commune, name="Attin", postal="62170", department=dpt_nord
    ).make()
    non_regional_actor = Recipe(auth.User).make()
    non_regional_actor.groups.add(st_group)
    non_regional_actor.profile.departments.add(dpt_npdc)

    user = Recipe(auth.User, username="auser", email="user@example.com").make()
    project = baker.make(
        models.Project,
        email=user.email,
        emails=[user.email],
        commune=commune,
        status="READY",
    )

    # Generate a notification
    signals.project_switchtender_joined.send(sender=regional_actor, project=project)

    assert regional_actor.notifications.unsent().count() == 1
    assert regional_actor2.notifications.unsent().count() == 1
    assert non_regional_actor.notifications.unsent().count() == 0

    digests.send_digest_for_switchtender_by_user(regional_actor)
    digests.send_digest_for_switchtender_by_user(regional_actor2)
    digests.send_digest_for_switchtender_by_user(non_regional_actor)

    assert regional_actor.notifications.unsent().count() == 0
    assert regional_actor2.notifications.unsent().count() == 0
    assert non_regional_actor.notifications.unsent().count() == 0


def test_notification_formatter():
    formatter = NotificationFormatter()

    user = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    organization = Recipe(addressbook_models.Organization, name="DuckCorp").make()
    user.profile.organization = organization
    user.profile.save()
    recipient = Recipe(auth.User).make()
    resource = Recipe(resources_models.Resource, title="Belle Ressource").make()
    task = Recipe(
        models.Task,
        intent="my intent",
        content="A very nice content",
        resource=resource,
    ).make()
    note = Recipe(
        models.Note,
        content="my content",
    ).make()
    followup = Recipe(models.TaskFollowup, task=task, comment="Hello!").make()
    project = Recipe(
        models.Project,
        name="Nice Project",
        description="Super description",
        location="SomeWhere",
    ).make()

    tests = [
        (
            "a créé une note de suivi",
            note,
            ("Bobi Joe (DuckCorp) a rédigé une note de suivi", "my content"),
        ),
        (
            "a commenté l'action",
            followup,
            (
                "Bobi Joe (DuckCorp) a commenté la recommandation 'Belle Ressource'",
                followup.comment,
            ),
        ),
        (
            "a recommandé l'action",
            task,
            ("Bobi Joe (DuckCorp) a recommandé 'Belle Ressource'", task.content),
        ),
        (
            "est devenu·e aiguilleur·se sur le projet",
            project,
            ("Bobi Joe (DuckCorp) s'est joint·e à l'équipe d'aiguillage.", None),
        ),
        (
            "a soumis pour modération le projet",
            project,
            (
                "Bobi Joe (DuckCorp) a soumis pour modération le projet 'Nice Project'",
                "Super description",
            ),
        ),
        (
            "a déposé le projet",
            project,
            (
                "Bobi Joe (DuckCorp) a déposé le projet 'Nice Project'",
                "Super description",
            ),
        ),
        (
            "action inconnue",
            project,
            ("Bob action inconnue Nice Project - SomeWhere", None),
        ),
    ]

    for test in tests:
        notify.send(
            sender=user,
            recipient=recipient,
            verb=test[0],
            action_object=test[1],
            target=project,
        )

    for idx, notification in enumerate(
        reversed(notifications_models.Notification.objects.all())
    ):
        fmt_reco = formatter.format(notification)
        assert tests[idx][2][0] == fmt_reco.summary
        assert tests[idx][2][1] == fmt_reco.excerpt


# eof
