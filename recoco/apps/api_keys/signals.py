from django.db.models.signals import post_save
from django.dispatch import receiver

from recoco.apps.home.models import UserProfile

from .models import ServiceAPIKey


@receiver(post_save, sender=UserProfile)
def delete_api_keys_of_non_bot_users(sender, instance, **kwargs):
    """A user who is not (or no longer) a bot must not keep any API key.

    Note: bulk ``UserProfile.objects.update(is_bot=False)`` bypasses this signal.
    """
    if not instance.is_bot:
        ServiceAPIKey.objects.filter(user_id=instance.user_id).delete()
