# encoding: utf-8

"""
Tests for communication application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-12-24 12:37:56 CEST
"""

from ..brevo import Brevo


def test_brevo_send_email_to_unique_recipient(mocker, client):
    brevo = Brevo()

    mocker.patch("sib_api_v3_sdk.TransactionalEmailsApi.send_transac_email")

    brevo.send_email(
        template_id=1,
        recipients={"name": "Bob", "email": "bob@example.com"},
        params={"p1": "v1"},
    )

    brevo.api_instance.send_transac_email.assert_called_once()


def test_brevo_send_email_to_multiple_recipients(mocker, client):
    brevo = Brevo()

    mocker.patch("sib_api_v3_sdk.TransactionalEmailsApi.send_transac_email")

    brevo.send_email(
        template_id=1,
        recipients=[
            {"name": "Bob", "email": "bob@example.com"},
            {"name": "Ana", "email": "ana@example.com"},
        ],
        params={"p1": "v1"},
    )

    brevo.api_instance.send_transac_email.assert_called_once()


def test_brevo_send_test_email(mocker, client):
    brevo = Brevo()

    mocker.patch("sib_api_v3_sdk.TransactionalEmailsApi.send_test_template")

    brevo.send_email(
        template_id=1,
        recipients={"name": "Bob", "email": "bob@example.com"},
        params={"p1": "v1"},
        test=True,
    )

    brevo.api_instance.send_test_template.assert_called_once()
