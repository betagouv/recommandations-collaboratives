import pytest
from model_bakery import baker

from .api import build_message_feed
from .models import ContactNode, DocumentNode, MarkdownNode, Message, RecommendationNode


######--- Message ----#####
@pytest.mark.django_db
def test_serialize_message_without_node():
    m = baker.make(Message)
    assert m.serialize()


@pytest.mark.django_db
def test_serialize_message_with_node():
    m = baker.make(Message)
    baker.make(MarkdownNode, message=m, text="hello ##title")

    payload = m.serialize()
    assert len(payload["nodes"]) == 1


######-- Nodes ---##########
@pytest.mark.django_db
def test_serialize_node_markdown():
    node = baker.make(MarkdownNode, text="hello ##title")

    payload = node.serialize()

    assert payload["type"] is MarkdownNode.NODE_TYPE
    assert payload["data"]["text"] == node.text


@pytest.mark.django_db
def test_serialize_node_contact():
    node = baker.make(ContactNode)

    payload = node.serialize()

    assert payload["type"] is ContactNode.NODE_TYPE
    assert payload["data"]["contact_id"] is not None


@pytest.mark.django_db
def test_serialize_node_document():
    node = baker.make(DocumentNode, document__the_link="http://blah.com")

    payload = node.serialize()

    assert payload["type"] is DocumentNode.NODE_TYPE
    assert payload["data"]["document_id"] is not None


@pytest.mark.django_db
def test_serialize_node_recommendation():
    node = baker.make(RecommendationNode)

    payload = node.serialize()

    assert payload["type"] is RecommendationNode.NODE_TYPE
    assert payload["data"]["text"] is not None
    assert payload["data"]["recommendation_id"] is not None


#####--- Feed ---#####
@pytest.mark.django_db
def test_build_message_feed():
    m = baker.make(Message)
    baker.make(MarkdownNode, message=m, text="hello ##title")

    assert build_message_feed(m.project)
