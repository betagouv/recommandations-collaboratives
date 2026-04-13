# encoding: utf-8

"""
Data migration to backfill activity traces for already-sent reminders.

For each sent Reminder, creates an actstream Action with the matching verb:
  - NEW_RECO: "a reçu un rappel de recommandations"
  - WHATS_UP: "a reçu un rappel de suivi de dossier"

"""

from django.db import migrations

# Duplicated from verbs to keep it self contained
VERB_BY_KIND = {
    0: "a reçu un rappel de recommandations",  # Reminder.NEW_RECO
    1: "a reçu un rappel de suivi de dossier",  # Reminder.WHATS_UP
}


def backfill_reminder_traces(apps, schema_editor):
    Reminder = apps.get_model("reminders", "Reminder")
    Action = apps.get_model("actstream", "Action")
    ContentType = apps.get_model("contenttypes", "ContentType")

    reminder_ct = ContentType.objects.get(app_label="reminders", model="reminder")
    project_ct = ContentType.objects.get(app_label="projects", model="project")
    user_ct = ContentType.objects.get(app_label="auth", model="user")

    reminders = (
        Reminder.objects.exclude(sent_on=None)
        .exclude(sent_to=None)
        .select_related("project", "site")
    )

    for reminder in reminders:
        verb = VERB_BY_KIND.get(reminder.kind)
        if verb is None:
            continue

        # skip if the action was already created
        already_exists = Action.objects.filter(
            actor_content_type=user_ct,
            actor_object_id=str(reminder.sent_to_id),
            verb=verb,
            action_object_content_type=reminder_ct,
            action_object_object_id=str(reminder.pk),
            site=reminder.site,
        ).exists()

        if already_exists:
            continue

        Action.objects.create(
            actor_content_type=user_ct,
            actor_object_id=str(reminder.sent_to_id),
            verb=verb,
            action_object_content_type=reminder_ct,
            action_object_object_id=str(reminder.pk),
            target_content_type=project_ct,
            target_object_id=str(reminder.project_id),
            timestamp=reminder.sent_on,
            public=False,
            site=reminder.site,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("reminders", "0013_reminder_kind_sent_on_site_project"),
        ("actstream", "0004_add_multisite_support"),
    ]

    operations = [
        migrations.RunPython(
            backfill_reminder_traces,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
