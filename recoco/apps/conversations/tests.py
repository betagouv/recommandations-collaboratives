import pytest
from model_bakery import baker

from .models import MarkdownNode, Message


@pytest.mark.django_db
def test_serialize_message_without_node():
    m = baker.make(Message)
    assert m.serialize()


@pytest.mark.django_db
def test_serialize_message_without_markdown():
    m = baker.make(Message)
    baker.make(MarkdownNode, message=m, text="hello ##title")

    payload = m.serialize()
    assert len(payload["nodes"]) == 1
