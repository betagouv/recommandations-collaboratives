# encoding: utf-8

"""
tests for digesting emails

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2022-02-03 16:14:54 CET
"""

from datetime import datetime, timezone
from unittest.mock import ANY, patch

import pytest
import test  # noqa
from django.contrib.auth import models as auth
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from freezegun import freeze_time
from model_bakery import baker
from model_bakery.recipe import Recipe
from notifications import models as notifications_models
from notifications.models import Notification
from notifications.signals import notify

from recoco import verbs
from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.communication.digests import (
    send_new_recommendations_reminders_digest_by_project,
    send_whatsup_reminders_digest_by_project,
)
from recoco.apps.conversations import models as conversations_models
from recoco.apps.geomatics import models as geomatics_models
from recoco.apps.home import models as home_models
from recoco.apps.projects import models as projects_models
from recoco.apps.projects import signals as projects_signals
from recoco.apps.projects.utils import assign_advisor, assign_collaborator
from recoco.apps.reminders.models import Reminder
from recoco.apps.resources import models as resources_models
from recoco.apps.tasks import models as tasks_models
from recoco.apps.tasks import signals as tasks_signals

from ...conversations.utils import gather_annotations_for_message_notification
from .. import digests

########################################################################
# new reco digests
########################################################################


@pytest.mark.django_db
def test_send_digests_for_new_reco_for_collaborators(client, request, make_project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    publishing_advisor = Recipe(
        auth.User, username="pub_advisor", email="pub-advisor@example.com"
    ).make()

    collaborator = Recipe(
        auth.User, username="collaborator", email="collab@example.com"
    ).make()

    project = make_project(
        site=current_site,
        status="TO_PROCESS",
    )

    assign_advisor(publishing_advisor, project, current_site)
    assign_collaborator(collaborator, project, is_owner=True)

    # Generate a notification
    tasks_signals.action_created.send(
        sender=test_send_digests_for_new_reco_for_collaborators,
        task=tasks_models.Task.objects.create(
            public=True,
            project=project,
            site=current_site,
            created_by=publishing_advisor,
        ),
        project=project,
        user=publishing_advisor,
    )

    assert collaborator.notifications.unsent().count() == 1

    digests.send_digests_for_new_recommendations_by_user(collaborator, dry_run=False)
    # FIXME: Replace with new call that handle message containing a recommendation

    assert collaborator.notifications.unsent().count() == 0


@pytest.mark.django_db
def test_send_digests_for_new_reco_should_not_trigger_for_advisors(
    client, request, make_project
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    publishing_advisor = Recipe(
        auth.User, username="pub_advisor", email="pub-advisor@example.com"
    ).make()

    another_advisor = Recipe(
        auth.User, username="another_advisor", email="another-advisor@example.com"
    ).make()

    collaborator = Recipe(
        auth.User, username="collaborator", email="collab@example.com"
    ).make()

    project = make_project(
        site=current_site,
        status="TO_PROCESS",
    )

    assign_advisor(publishing_advisor, project, current_site)
    assign_advisor(another_advisor, project, current_site)
    assign_collaborator(collaborator, project, is_owner=True)

    # Generate a notification
    tasks_signals.action_created.send(
        sender=test_send_digests_for_new_reco_should_not_trigger_for_advisors,
        task=tasks_models.Task.objects.create(
            public=True,
            project=project,
            site=current_site,
            created_by=publishing_advisor,
        ),
        project=project,
        user=publishing_advisor,
    )

    assert publishing_advisor.notifications.unsent().count() == 0
    assert another_advisor.notifications.unsent().count() == 1

    digests.send_digests_for_new_recommendations_by_user(another_advisor, dry_run=False)

    assert publishing_advisor.notifications.unsent().count() == 0
    assert another_advisor.notifications.unsent().count() == 1


@pytest.mark.django_db
def test_send_digests_for_new_reco_empty(client, request, make_project):
    site = get_current_site(request)
    membership = baker.make(projects_models.ProjectMember)

    make_project(site=site, status="DONE", projectmember_set=[membership])

    digests.send_digests_for_new_recommendations_by_user(
        membership.member, dry_run=False
    )

    assert membership.member.notifications.unsent().count() == 0


@pytest.mark.django_db
def test_make_site_digest_with_siteconfiguration(client, request):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    data = digests.make_site_digest(site)

    assert "legal_owner" in data

    assert len(data) > 0


@pytest.mark.django_db
def test_make_project_survey_for_site_digest_without_configuration(
    project_ready, client, request
):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)
    user = Recipe(auth.User).make()
    data = digests.make_project_survey_digest_for_site(user, project_ready, site)

    assert len(data) > 0
    assert data["name"] is None


@pytest.mark.django_db
def test_make_project_survey_for_site_digest_with_configuration(
    project_ready, client, request
):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, project_survey__name="Survey", site=site)
    user = Recipe(auth.User).make()
    data = digests.make_project_survey_digest_for_site(user, project_ready, site)

    assert len(data) > 0
    assert data["name"] is not None


########################################################################
# new sites digests
########################################################################


@pytest.mark.django_db
def test_send_digests_for_new_sites_by_user(request, make_project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    advisor_group = auth.Group.objects.get(name="example_com_advisor")

    # regional actor
    dpt_nord = Recipe(geomatics_models.Department, code=59, name="Nord").make()
    commune = Recipe(
        geomatics_models.Commune, name="Lille", postal="59000", department=dpt_nord
    ).make()
    regional_actor = Recipe(auth.User).make()
    regional_actor.groups.add(advisor_group)
    regional_actor.profile.departments.add(dpt_nord)
    regional_actor.profile.sites.add(current_site)

    # non regional actor
    dpt_npdc = Recipe(geomatics_models.Department, code=62, name="PDC").make()
    commune = Recipe(
        geomatics_models.Commune, name="Attin", postal="62170", department=dpt_nord
    ).make()
    non_regional_actor = Recipe(auth.User).make()
    non_regional_actor.groups.add(advisor_group)
    non_regional_actor.profile.departments.add(dpt_npdc)
    non_regional_actor.profile.sites.add(current_site)

    # moderator
    moderator = Recipe(auth.User).make()

    membership = baker.make(projects_models.ProjectMember, is_owner=True)
    project = make_project(
        projectmember_set=[membership],
        commune=commune,
        status="READY",
        site=current_site,
    )

    # Generate a notification
    projects_signals.project_validated.send(
        sender=projects_models.Project,
        site=current_site,
        moderator=moderator,
        project=project,
    )

    assert regional_actor.notifications.unsent().count() == 1
    assert non_regional_actor.notifications.unsent().count() == 0

    digests.send_digests_for_new_sites_by_user(regional_actor)
    digests.send_digests_for_new_sites_by_user(non_regional_actor)

    assert regional_actor.notifications.unsent().count() == 0
    assert non_regional_actor.notifications.unsent().count() == 0


@pytest.mark.django_db
def test_send_digests_for_switchtender_by_user(request, client, make_project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    advisor_group = auth.Group.objects.get(name="example_com_advisor")

    # regional actor
    dpt_nord = Recipe(geomatics_models.Department, code=59, name="Nord").make()
    commune = Recipe(
        geomatics_models.Commune, name="Lille", postal="59000", department=dpt_nord
    ).make()

    organization = Recipe(addressbook_models.Organization, name="Orga").make()
    regional_actor = Recipe(auth.User).make()
    regional_actor.profile.sites.add(current_site)
    regional_actor.profile.organization = organization
    regional_actor.profile.save()
    regional_actor.groups.add(advisor_group)
    regional_actor.profile.departments.add(dpt_nord)

    regional_actor2 = Recipe(auth.User).make()
    regional_actor2.groups.add(advisor_group)
    regional_actor2.profile.departments.add(dpt_nord)
    regional_actor2.profile.sites.add(current_site)

    # non regional actor
    dpt_npdc = Recipe(geomatics_models.Department, code=62, name="PDC").make()
    commune = Recipe(
        geomatics_models.Commune, name="Attin", postal="62170", department=dpt_nord
    ).make()
    non_regional_actor = Recipe(auth.User).make()
    non_regional_actor.groups.add(advisor_group)
    non_regional_actor.profile.departments.add(dpt_npdc)
    non_regional_actor.profile.sites.add(current_site)

    membership = baker.make(projects_models.ProjectMember, is_owner=True)
    project = make_project(
        projectmember_set=[membership],
        commune=commune,
        site=current_site,
        status="READY",
    )

    # Generate a notification
    projects_signals.project_switchtender_joined.send(
        sender=regional_actor, project=project
    )

    assert (
        regional_actor.notifications.unsent().count() == 0
    )  # shouldn't get her own action notified
    assert regional_actor2.notifications.unsent().count() == 0
    assert non_regional_actor.notifications.unsent().count() == 0
    assert membership.member.notifications.unsent().count() == 1

    digests.send_digest_for_switchtender_by_user(regional_actor)
    digests.send_digest_for_switchtender_by_user(regional_actor2)
    digests.send_digest_for_switchtender_by_user(non_regional_actor)

    assert regional_actor.notifications.unsent().count() == 0
    assert regional_actor2.notifications.unsent().count() == 0
    assert non_regional_actor.notifications.unsent().count() == 0


@pytest.mark.django_db
def test_send_digests_for_switchtender_includes_new_recos(
    client, request, make_project
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    publishing_advisor = Recipe(
        auth.User, username="pub_advisor", email="pub-advisor@example.com"
    ).make()

    another_advisor = Recipe(
        auth.User, username="another_advisor", email="another-advisor@example.com"
    ).make()

    collaborator = Recipe(
        auth.User, username="collaborator", email="collab@example.com"
    ).make()

    project = make_project(
        site=current_site,
        status="TO_PROCESS",
    )

    assign_advisor(publishing_advisor, project, current_site)
    assign_advisor(another_advisor, project, current_site)
    assign_collaborator(collaborator, project, is_owner=True)

    # Generate a notification
    tasks_signals.action_created.send(
        sender=test_send_digests_for_new_reco_should_not_trigger_for_advisors,
        task=tasks_models.Task.objects.create(
            public=True,
            project=project,
            site=current_site,
            created_by=publishing_advisor,
        ),
        project=project,
        user=publishing_advisor,
    )

    assert another_advisor.notifications.unsent().count() == 1

    digests.send_digest_for_switchtender_by_user(another_advisor)

    assert another_advisor.notifications.unsent().count() == 0


@pytest.mark.django_db
def test_notification_formatter(request, make_project):
    formatter = digests.NotificationFormatter()

    user = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    organization = Recipe(addressbook_models.Organization, name="DuckCorp").make()
    user.profile.organization = organization
    user.profile.save()
    recipient = Recipe(auth.User).make()
    resource = Recipe(resources_models.Resource, title="Belle Ressource").make()
    project = make_project(site=get_current_site(request), name="Nice Project")
    task = Recipe(
        tasks_models.Task,
        intent="my intent",
        project=project,
        content="A very nice content",
        resource=resource,
    ).make()
    public_note = Recipe(projects_models.Note, content="my content", public=True).make()
    private_note = Recipe(
        projects_models.Note, content="my content", public=False
    ).make()

    followup = Recipe(tasks_models.TaskFollowup, task=task, comment="Hello!").make()

    tests = [
        (
            verbs.Conversation.PUBLIC_MESSAGE,
            public_note,
            (
                f"Bobi Joe (DuckCorp) {verbs.Conversation.PUBLIC_MESSAGE}",
                "my content",
            ),
        ),
        (
            verbs.Conversation.PRIVATE_MESSAGE,
            private_note,
            (
                f"Bobi Joe (DuckCorp) {verbs.Conversation.PRIVATE_MESSAGE}",
                "my content",
            ),
        ),
        (
            verbs.Recommendation.COMMENTED,
            followup,
            (
                f"Bobi Joe (DuckCorp) {verbs.Recommendation.COMMENTED} "
                "'Belle Ressource'",
                followup.comment,
            ),
        ),
        (
            verbs.Recommendation.CREATED,
            task,
            (
                f"Bobi Joe (DuckCorp) {verbs.Recommendation.CREATED} 'Belle Ressource'",
                task.content,
            ),
        ),
        (
            verbs.Project.BECAME_ADVISOR,
            project,
            (
                f"Bobi Joe (DuckCorp) {verbs.Project.BECAME_ADVISOR}.",
                None,
            ),
        ),
        (
            verbs.Project.BECAME_OBSERVER,
            project,
            (
                f"Bobi Joe (DuckCorp) {verbs.Project.BECAME_OBSERVER}.",
                None,
            ),
        ),
        (
            verbs.Project.SUBMITTED_BY,
            project,
            (
                f"Bobi Joe (DuckCorp) {verbs.Project.SUBMITTED_BY}: 'Nice Project'",
                "Super description",
            ),
        ),
        (
            verbs.Project.AVAILABLE,  # FIXME redondant avec VALIDATED
            project,
            (
                f"Bobi Joe (DuckCorp) {verbs.Project.AVAILABLE} 'Nice Project'",
                "Super description",
            ),
        ),
        (
            verbs.Document.ADDED,  # FIXME replace w/ ADDED_FILE ADDED_LINK
            project,
            (
                f"Bobi Joe (DuckCorp) {verbs.Document.ADDED}",
                None,
            ),
        ),
        (
            "action inconnue",
            project,
            (
                "Bob action inconnue Nice Project - SomeWhere",
                None,
            ),
        ),
    ]

    for t in tests:
        notify.send(
            sender=user,
            recipient=recipient,
            verb=t[0],
            action_object=t[1],
            target=project,
        )

    for idx, notification in enumerate(
        reversed(notifications_models.Notification.objects.all())
    ):
        fmt_reco = formatter.format(notification)
        assert tests[idx][2][0] == fmt_reco.summary
        assert tests[idx][2][1] == fmt_reco.excerpt


@pytest.mark.django_db
def test_notification_formatter_with_bogus_user():
    formatter = digests.NotificationFormatter()

    user = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    note = Recipe(projects_models.Note).make()

    notification = Notification(
        user, verb=verbs.Conversation.PUBLIC_MESSAGE, action_object=note
    )

    fmt_reco = formatter.format(notification)
    assert "compte indisponible" in str(fmt_reco)


@pytest.mark.django_db
class TestMsgDigest:
    def prepare(self, project_ready, current_site):
        recipient = baker.make(User)
        sender = baker.make(User, last_name="Lexpère", first_name="Mosio")
        project_ready.members.add(recipient)
        project_ready.members.add(sender)
        contact1 = baker.make(
            addressbook_models.Contact, first_name="Léa", last_name="Bonchancel"
        )
        contact2 = baker.make(addressbook_models.Contact)
        doc = baker.make(projects_models.Document, the_link="something")
        reco = baker.make(tasks_models.Task, site=current_site, intent="Holala fais ça")

        msg1 = baker.make(
            conversations_models.Message, posted_by=sender, project=project_ready
        )
        msg2 = baker.make(
            conversations_models.Message, posted_by=sender, project=project_ready
        )
        (
            conversations_models.ContactNode.objects.create(
                contact=contact1, position=1, message=msg1
            ),
        )
        conversations_models.DocumentNode.objects.create(
            document=doc, position=2, message=msg1
        )
        (
            conversations_models.ContactNode.objects.create(
                contact=contact2, position=1, message=msg2
            ),
        )
        conversations_models.MarkdownNode.objects.create(
            text="toto", position=2, message=msg2
        )
        conversations_models.RecommendationNode.objects.create(
            recommendation=reco, position=3, message=msg2
        )

        notifs = [
            {
                "sender": sender,
                "verb": verbs.Conversation.POST_MESSAGE,
                "action_object": msg1,
                "target": project_ready,
                "annotations": gather_annotations_for_message_notification(msg1),
            },
            {
                "sender": sender,
                "verb": verbs.Conversation.POST_MESSAGE,
                "action_object": msg2,
                "target": project_ready,
                "annotations": gather_annotations_for_message_notification(msg2),
            },
        ]
        for notif in notifs:
            notify.send(
                recipient=[recipient],
                site=current_site,
                **notif,
            )

        return recipient, sender, contact1, [msg1, msg2]

    def test_send_msg_digest(self, project_ready, current_site):
        (recipient, sender, first_object, [msg1, msg2]) = self.prepare(
            project_ready, current_site
        )
        baker.make(home_models.SiteConfiguration, site=current_site)

        assert recipient.notifications.unsent().count() == 2
        digests.send_msg_digest_by_user_and_project(
            project_ready, recipient, current_site, dry_run=False
        )
        assert recipient.notifications.unsent().count() == 0

    def test_make_msg_digest(self, project_ready, current_site):
        (recipient, sender, first_object, [msg1, msg2]) = self.prepare(
            project_ready, current_site
        )

        expected = {
            "first_object": {
                "email": "",
                "first_name": "Léa",
                "function": "",
                "last_name": "Bonchancel",
                "mobile_no": "",
                "organization_name": first_object.organization.name,
                "phone_no": "",
                "type": "contact",
            },
            "first_sender": {
                "first_name": "Mosio",
                "first_name_initial": "M",
                "image": "https://secure.gravatar.com/avatar/d41d8cd98f00b204e9800998ecf8427e.jpg?s=50&d=mm&r=g",
                "last_name": "Lexpère",
                "organization": "",
                "pk": sender.id,
                "short": "M. Lexpère",
            },
            "intro_count": "1 message, 2 contacts, 1 recommendation et 1 document",
            "other_senders": True,
            "remaining_count": "1 contact, 1 recommendation et 1 document",
            "site_name": "example.com",
            "text": "toto",
            "title_count": "2 nouveaux messages",
        }

        digest = digests.make_msg_digest_by_user_and_project(
            Notification.objects.all(), recipient, project_ready, current_site
        )

        # project's digest should be tested else where
        del digest["project"]
        assert digest["message_url"].startswith(
            f"https://example.com/project/{project_ready.id}/conversations?message-id={msg1.id}"
        )
        del digest["message_url"]
        assert digest == expected


@pytest.mark.django_db
@patch("recoco.apps.communication.digests.make_or_update_new_recommendations_reminder")
@patch(
    "recoco.apps.communication.digests.get_due_new_recommendations_reminder_for_project"
)
@patch("recoco.apps.communication.digests.make_digest_of_project_recommendations")
class TestSendNewRecommendationsRemindersDigestByProject:
    def test_dryrun(
        self, mock_make_digest, mock_get_due_reminder, mock_make_reminder, current_site
    ):
        project = baker.make(projects_models.Project, sites=[current_site])
        res = send_new_recommendations_reminders_digest_by_project(
            site=current_site, project=project, dry_run=True
        )

        assert res is True
        mock_make_reminder.assert_called_once_with(current_site, project)
        mock_get_due_reminder.assert_called_once_with(current_site, project)
        mock_make_digest.assert_not_called()

    def test_no_due_reminder(
        self, mock_make_digest, mock_get_due_reminder, mock_make_reminder, current_site
    ):
        mock_get_due_reminder.return_value = baker.make(Reminder)

        project = baker.make(projects_models.Project, sites=[current_site])
        res = send_new_recommendations_reminders_digest_by_project(
            site=current_site, project=project, dry_run=False
        )

        assert res is False
        mock_make_reminder.assert_called_once_with(current_site, project)
        mock_get_due_reminder.assert_called_once_with(current_site, project)
        mock_make_digest.assert_not_called()

    def test_no_project_owner(
        self, mock_make_digest, mock_get_due_reminder, mock_make_reminder, current_site
    ):
        project = baker.make(projects_models.Project, sites=[current_site])
        project.projectmember_set.all().delete()

        res = send_new_recommendations_reminders_digest_by_project(
            site=current_site, project=project, dry_run=False
        )

        assert res is False
        mock_make_digest.assert_not_called()

    @freeze_time("2025-04-10 08:00:00")
    def test_digest_sent(
        self, mock_make_digest, mock_get_due_reminder, mock_make_reminder, current_site
    ):
        due_reminder = baker.make(Reminder)
        project = baker.make(projects_models.Project, sites=[current_site])
        owner = baker.make(
            auth.User,
            email="anakin@jedi.com",
            first_name="Anakin",
            last_name="Skywalker",
        )
        baker.make(
            projects_models.ProjectMember, project=project, is_owner=True, member=owner
        )

        mock_get_due_reminder.return_value = due_reminder
        mock_make_digest.return_value = {"any": "digest"}

        with patch("recoco.apps.communication.digests.send_email") as mock_send_email:
            res = send_new_recommendations_reminders_digest_by_project(
                site=current_site, project=project, dry_run=False
            )

        assert res is True
        mock_make_reminder.assert_called_once_with(current_site, project)
        mock_get_due_reminder.assert_called_once_with(current_site, project)
        mock_make_digest.assert_called_once_with(project, ANY, owner)

        mock_send_email.assert_called_once_with(
            template_name="project_reminders_new_reco_digest",
            recipients={
                "name": "Anakin Skywalker",
                "email": "anakin@jedi.com",
            },
            params={"any": "digest"},
            related=due_reminder,
        )

        due_reminder.refresh_from_db()
        assert due_reminder.sent_to == owner
        assert due_reminder.sent_on == datetime(
            2025, 4, 10, 8, 0, 0, tzinfo=timezone.utc
        )


@pytest.mark.django_db
@patch("recoco.apps.communication.digests.make_or_update_whatsup_reminder")
@patch("recoco.apps.communication.digests.get_due_whatsup_reminder_for_project")
@patch("recoco.apps.communication.digests.make_digest_of_project_recommendations")
class TestSendWhatsupRemindersDigestByProject:
    def test_dryrun(
        self, mock_make_digest, mock_get_due_reminder, mock_make_reminder, current_site
    ):
        project = baker.make(projects_models.Project, sites=[current_site])
        res = send_whatsup_reminders_digest_by_project(
            site=current_site, project=project, dry_run=True
        )

        assert res is True
        mock_make_reminder.assert_called_once_with(current_site, project)
        mock_get_due_reminder.assert_called_once_with(current_site, project)
        mock_make_digest.assert_not_called()

    def test_no_due_reminder(
        self, mock_make_digest, mock_get_due_reminder, mock_make_reminder, current_site
    ):
        mock_get_due_reminder.return_value = baker.make(Reminder)

        project = baker.make(projects_models.Project, sites=[current_site])
        res = send_whatsup_reminders_digest_by_project(
            site=current_site, project=project, dry_run=False
        )

        assert res is False
        mock_make_reminder.assert_called_once_with(current_site, project)
        mock_get_due_reminder.assert_called_once_with(current_site, project)
        mock_make_digest.assert_not_called()

    def test_no_project_owner(
        self, mock_make_digest, mock_get_due_reminder, mock_make_reminder, current_site
    ):
        project = baker.make(projects_models.Project, sites=[current_site])
        project.projectmember_set.all().delete()

        res = send_whatsup_reminders_digest_by_project(
            site=current_site, project=project, dry_run=False
        )

        assert res is False
        mock_make_digest.assert_not_called()

    @freeze_time("2025-04-10 08:00:00")
    def test_digest_sent(
        self, mock_make_digest, mock_get_due_reminder, mock_make_reminder, current_site
    ):
        due_reminder = baker.make(Reminder)
        project = baker.make(projects_models.Project, sites=[current_site])
        owner = baker.make(
            auth.User,
            email="anakin@jedi.com",
            first_name="Anakin",
            last_name="Skywalker",
        )
        baker.make(
            projects_models.ProjectMember, project=project, is_owner=True, member=owner
        )

        mock_get_due_reminder.return_value = due_reminder
        mock_make_digest.return_value = {"any": "digest"}

        with patch("recoco.apps.communication.digests.send_email") as mock_send_email:
            res = send_whatsup_reminders_digest_by_project(
                site=current_site, project=project, dry_run=False
            )

        assert res is True
        mock_make_reminder.assert_called_once_with(current_site, project)
        mock_get_due_reminder.assert_called_once_with(current_site, project)
        mock_make_digest.assert_called_once_with(project, ANY, owner)

        mock_send_email.assert_called_once_with(
            template_name="project_reminders_whats_up_digest",
            recipients={
                "name": "Anakin Skywalker",
                "email": "anakin@jedi.com",
            },
            params={"any": "digest"},
            related=due_reminder,
        )

        due_reminder.refresh_from_db()
        assert due_reminder.sent_to == owner
        assert due_reminder.sent_on == datetime(
            2025, 4, 10, 8, 0, 0, tzinfo=timezone.utc
        )


# eof
