from django.contrib.auth import models as auth
from model_bakery import baker
from model_bakery.recipe import Recipe

from .. import digests, models, signals


def test_make_digest_for_new_reco(client):
    user = Recipe(auth.User, username="auser", email="user@example.com").make()
    switchtender = Recipe(
        auth.User, username="switchtender", email="switchtender@example.com"
    ).make()
    project = baker.make(models.Project, status="READY", emails=[user.email])

    # Generate a notification
    signals.action_created.send(
        sender=test_make_digest_for_new_reco,
        task=models.Task.objects.create(project=project, created_by=switchtender),
        project=project,
        user=switchtender,
    )

    digests.send_digests_for_new_recommendations_by_user(user)

    assert user.notifications.unsent().count() == 0
