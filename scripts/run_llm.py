#!/usr/bin/env python3
import lmstudio
import pytest
import requests

API_URL = "http://urbanvitaliz.localhost:8000/api/ml/summaries"


def query_llm(content, config, prompt):
    model = lmstudio.llm()

    chat = lmstudio.Chat(prompt)
    chat.add_user_message(content)

    return model.respond(chat)


def fetch_summary(session, summary_id):
    r = session.get(f"{API_URL}/{summary_id}/")

    r.raise_for_status()

    return r.json()


def write_summary_text(session, summary_id, text):
    r = session.patch(f"{API_URL}/{summary_id}/", data={"text": text})

    r.raise_for_status()

    return r.json()


def summarize(session, summary_id):
    summary = fetch_summary(session, summary_id)
    text = query_llm(
        summary["original_content"], summary["config"], summary["prompt"]["text"]
    )
    return write_summary_text(session, summary_id, text)


if __name__ == "__main__":
    s = requests.Session()
    s.auth = ("ml_access", "jadorelesmls123")


## TESTS
@pytest.fixture
def session():
    s = requests.Session()
    s.auth = ("ml_access", "jadorelesmls123")
    return s


def test_fetch_summary(session):
    assert "original_content" in fetch_summary(session, 1)


def test_write_summary(session):
    write_summary_text(session, 1, "coucou")


def test_query_llm(session):
    response = query_llm(
        "Qui est le partenaire de Minus ?",
        None,
        "You are a french expert in comics, reply with only a few words, in French.",
    )
    assert response


def test_summarize(session):
    summary = summarize(session, 1)
    assert summary["text"]
