from .models import Message


def build_feed(project):
    messages = Message.objects.filter(project=project).order_by("created")

    feed = [message.serialize() for message in messages]

    return feed
