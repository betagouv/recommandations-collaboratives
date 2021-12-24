# encoding: utf-8

"""
Tests for communication application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-12-24 12:37:56 CEST
"""

from .sendinblue import SendInBlue


def test_sib_send_email_to_unique_recipient(mocker, client):
    sib = SendInBlue()

    mocker.patch("sib_api_v3_sdk.TransactionalEmailsApi.send_transac_email")

    sib.send_email(template_id=1, recipients="bob@example.com", params={"p1": "v1"})

    sib.api_instance.send_transac_email.assert_called_once()


def test_sib_send_email_to_multiple_recipients(mocker, client):
    sib = SendInBlue()

    mocker.patch("sib_api_v3_sdk.TransactionalEmailsApi.send_transac_email")

    sib.send_email(
        template_id=1,
        recipients=["bob@example.com", "ana@example.com"],
        params={"p1": "v1"},
    )

    sib.api_instance.send_transac_email.assert_called_once()


def test_sib_send_test_email(mocker, client):
    sib = SendInBlue()

    mocker.patch("sib_api_v3_sdk.TransactionalEmailsApi.send_test_template")

    sib.send_email(
        template_id=1, recipients="bob@example.com", params={"p1": "v1"}, test=True
    )

    sib.api_instance.send_test_template.assert_called_once()
