from notifications.models import Notification

from recoco import verbs

mapping = [
    (
        "a rejoint le dossier",
        verbs.Project.JOINED,
    ),
    (
        "a déposé un nouveau dossier, qui est en attente de validation",
        verbs.Project.SUBMITTED_BY,
    ),
]

for old, new in mapping:
    for notification in Notification.objects.filter(verb__icontains=old):
        print(
            f"Updating notification {notification.id} verb from '{notification.verb}' to '{new}'"
        )
        notification.verb = new
        notification.save()
