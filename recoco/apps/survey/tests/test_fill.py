# encoding: utf-8

"""
Tests for survey application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-27 12:06:10 CEST
"""

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertRedirects

from recoco.apps.home import models as home_models
from recoco.apps.onboarding import models as onboarding_models
from recoco.apps.projects import models as projects
from recoco.apps.projects.utils import assign_advisor, assign_collaborator
from recoco.utils import login

from .. import models

########################################################################
# creating sessions
########################################################################


@pytest.mark.django_db
def test_new_survey_session_is_created(request, client, project):
    current_site = get_current_site(request)
    survey = Recipe(models.Survey, site=current_site).make()

    onboarding = onboarding_models.Onboarding.objects.first()

    Recipe(
        home_models.SiteConfiguration,
        site=current_site,
        onboarding=onboarding,
        project_survey=survey,
    ).make()

    url = reverse("survey-project-session", args=(project.id,))
    with login(client, is_staff=False):
        response = client.get(url)

    new_session = models.Session.objects.get(survey=survey, project=project)

    assert response.status_code == 302
    assert response.url == reverse("survey-session-start", args=(new_session.id,))


@pytest.mark.django_db
def test_existing_survey_session_is_reused(request, client, project):
    current_site = get_current_site(request)
    survey = Recipe(models.Survey, site=current_site).make()

    onboarding = onboarding_models.Onboarding.objects.first()

    Recipe(
        home_models.SiteConfiguration,
        site=current_site,
        onboarding=onboarding,
        project_survey=survey,
    ).make()

    session = Recipe(models.Session, project=project, survey=survey).make()

    url = reverse("survey-project-session", args=(project.id,))
    with login(client, is_staff=False):
        response = client.get(url)

    new_session = models.Session.objects.get(survey=survey, project=project)

    assert new_session == session
    assert response.status_code == 302
    assert response.url == reverse("survey-session-start", args=(new_session.id,))


@pytest.mark.skip(reason="to be written")
@pytest.mark.django_db
def test_on_survey_creation_signal_is_sent(client):
    pass


########################################################################
# answering questions
########################################################################


@pytest.mark.django_db
def test_answered_question_with_comment_only_is_saved_to_session(
    request, client, project
):
    current_site = get_current_site(request)
    survey = Recipe(models.Survey, site=current_site).make()
    session = Recipe(models.Session, survey=survey, project=project).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()

    my_comment = "this is a comment"
    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"comment": my_comment})

    # Fetch persisted answer
    answer = models.Answer.objects.get(session=session, question=q1)
    assert answer.comment == my_comment


@pytest.mark.django_db
def test_answered_question_with_upload_has_attachment_saved(request, client):
    current_site = get_current_site(request)
    survey = Recipe(models.Survey, site=current_site).make()
    session = Recipe(
        models.Session, survey=survey, project__sites=[current_site]
    ).make()

    the_file = SimpleUploadedFile("test.pdf", b"Some content.")
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs, upload_title="The upload").make()
    Recipe(models.Question, question_set=qs).make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"comment": "blah", "attachment": the_file})

    # Fetch persisted answer
    answer = models.Answer.objects.get(session=session, question=q1)
    assert answer.attachment.size > 0


@pytest.mark.django_db
def test_answer_question_with_upload_only_keeps_attachment(request, client):
    current_site = get_current_site(request)
    survey = Recipe(models.Survey, site=current_site).make()
    session = Recipe(
        models.Session, survey=survey, project__sites=[current_site]
    ).make()

    the_file = SimpleUploadedFile("test.pdf", b"Some content.")
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs, upload_title="The upload").make()
    Recipe(models.Question, question_set=qs).make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        response = client.post(url, data={"attachment": the_file})

    assert response.status_code == 200
    assert "test.pdf" in str(response.content)


@pytest.mark.django_db
def test_answered_question_with_single_choice_is_saved_to_session(request, client):
    survey = Recipe(models.Survey, site=get_current_site(request)).make()
    session = Recipe(models.Session, survey=survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()
    choice = Recipe(models.Choice, question=q1, value="yep").make()
    Recipe(models.Choice, question=q1, value="nope").make()

    my_comment = "this is a comment"
    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"answer": choice.value, "comment": my_comment})

    # Fetch persisted answer
    answer = models.Answer.objects.get(session=session, question=q1)
    assert answer.values == [choice.value]
    assert answer.comment == my_comment


@pytest.mark.django_db
def test_answered_question_with_multiple_choice_is_saved_to_session(request, client):
    current_site = get_current_site(request)
    survey = Recipe(models.Survey, site=current_site).make()
    session = Recipe(
        models.Session, survey=survey, project__sites=[current_site]
    ).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, is_multiple=True, question_set=qs).make()
    choice = Recipe(models.Choice, question=q1, value="a").make()
    Recipe(models.Choice, question=q1, value="b").make()

    my_comment = "this is a comment"
    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"answer": [choice.value], "comment": my_comment})

    # Fetch persisted answer
    answer = models.Answer.objects.get(session=session, question=q1)
    assert answer.values == [choice.value]
    assert answer.comment == my_comment


@pytest.mark.django_db
def test_question_with_comment_only_make_comment_field_mandatory(client):
    survey = Recipe(models.Survey).make()
    session = Recipe(models.Session, survey=survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={})

    with pytest.raises(models.Answer.DoesNotExist):
        models.Answer.objects.get(session=session, question=q1)


@pytest.mark.django_db
def test_question_with_single_choice_signals_are_copied_over_answer(request, client):
    current_site = get_current_site(request)
    survey = Recipe(models.Survey, site=current_site).make()
    session = Recipe(
        models.Session, survey=survey, project__sites=[current_site]
    ).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()
    choice = Recipe(
        models.Choice, question=q1, value="yep", signals="lima-charlie, bravo-zulu"
    ).make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"answer": choice.value})

    # Fetch persisted answer
    answer = models.Answer.objects.get(session=session, question=q1)
    assert answer.signals == choice.signals


@pytest.mark.django_db
def test_question_with_single_multiple_signals_are_copied_over_answer(request, client):
    current_site = get_current_site(request)
    survey = Recipe(models.Survey, site=current_site).make()
    session = Recipe(models.Session, survey=survey).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, is_multiple=True, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()
    c1 = Recipe(
        models.Choice, question=q1, value="a", signals="lima-charlie, bravo-zulu"
    ).make()
    c2 = Recipe(models.Choice, question=q1, value="b", signals="alpha-tango").make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"answer": [c1.value, c2.value]})

    # Fetch persisted answer
    answer = models.Answer.objects.get(session=session, question=q1)
    assert set(answer.signals) == set(f"{c1.signals}, {c2.signals}")


@pytest.mark.django_db
def test_answered_question_is_updated_to_session(request, client):
    """Make sure we update and don't duplicate Answer when answering again"""
    current_site = get_current_site(request)
    survey = Recipe(models.Survey, site=current_site).make()
    session = Recipe(
        models.Session, survey=survey, project__sites=[current_site]
    ).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()

    my_signals = "oscar-mike"
    my_comment = "this is a comment"

    choice1 = Recipe(
        models.Choice, question=q1, value="nope", signals="november-golf"
    ).make()
    choice2 = Recipe(models.Choice, question=q1, value="yep", signals=my_signals).make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"answer": choice1.value})

        answer = models.Answer.objects.get(session=session, question=q1)
        updated_on_creation = answer.updated_on

        client.post(url, data={"answer": choice2.value, "comment": my_comment})

    # Fetch persisted answer
    assert models.Answer.objects.filter(session=session, question=q1).count() == 1

    answer = models.Answer.objects.get(session=session, question=q1)
    assert answer.values == [choice2.value]
    assert answer.comment == my_comment
    assert answer.signals == my_signals
    assert answer.updated_on > updated_on_creation


@pytest.mark.django_db
def test_question_redirects_to_next_question(request, client):
    current_site = get_current_site(request)
    survey = Recipe(models.Survey, site=current_site).make()
    session = Recipe(
        models.Session, survey=survey, project__sites=[current_site]
    ).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    choice = Recipe(models.Choice, question=q1, value="yep").make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        response = client.post(url, data={"answer": choice.value})

    assert response.status_code == 302
    assert response.url == reverse("survey-question-next", args=(session.id, q1.id))


@pytest.mark.django_db
def test_answered_question_triggers_notification(request, client):
    current_site = get_current_site(request)
    survey = Recipe(models.Survey, site=current_site).make()
    session = Recipe(models.Session, survey=survey).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()
    choice = Recipe(models.Choice, question=q1, value="yep").make()
    Recipe(models.Choice, question=q1, value="nope").make()

    my_comment = "this is a comment"
    url = reverse("survey-question-details", args=(session.id, q1.id))

    st = Recipe(auth_models.User).make()
    assign_advisor(st, session.project, current_site)

    with login(client, is_staff=False) as user:
        client.post(url, data={"answer": choice.value, "comment": my_comment})

    assert user.notifications.unread().count() == 0
    assert st.notifications.unread().count() == 1


@pytest.mark.django_db
def test_answered_question_debounces_notification(request, client):
    current_site = get_current_site(request)
    survey = Recipe(models.Survey, site=current_site).make()
    session = Recipe(models.Session, survey=survey).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()
    choice = Recipe(models.Choice, question=q1, value="yep").make()
    Recipe(models.Choice, question=q1, value="nope").make()

    my_comment = "this is a comment"
    url = reverse("survey-question-details", args=(session.id, q1.id))

    st = Recipe(auth_models.User).make()
    assign_advisor(st, session.project, current_site)

    with login(client, is_staff=False) as user:
        client.post(url, data={"answer": choice.value, "comment": my_comment})
        client.post(url, data={"answer": choice.value, "comment": my_comment})

    assert user.notifications.unread().count() == 0
    assert st.notifications.unread().count() == 1


########################################################################
# navigating questions
########################################################################


@pytest.mark.django_db
def test_next_question_redirects_to_next_available_question(request, client):
    survey = Recipe(models.Survey, site=get_current_site(request)).make()
    session = Recipe(models.Session, survey=survey).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    q2 = Recipe(models.Question, question_set=qs).make()

    with login(client, is_staff=False):
        url = reverse("survey-question-next", args=(session.id, q1.id))
        response = client.get(url)

    new_url = reverse("survey-question-details", args=(session.id, q2.id))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_next_question_redirects_to_done_when_no_more_questions(request, client):
    survey = Recipe(models.Survey, site=get_current_site(request)).make()
    session = Recipe(models.Session, survey=survey).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()

    with login(client, is_staff=False):
        url = reverse("survey-question-next", args=(session.id, q1.id))
        response = client.get(url)

    assert response.status_code == 302


@pytest.mark.django_db
def test_next_question_redirects_to_next_question_set(request, client):
    survey = Recipe(models.Survey, site=get_current_site(request)).make()
    session = Recipe(models.Session, survey=survey).make()
    qs1 = Recipe(models.QuestionSet, survey=survey, priority=30).make()
    q1 = Recipe(models.Question, question_set=qs1).make()

    qs2 = Recipe(models.QuestionSet, survey=survey, priority=10).make()
    Recipe(models.Question, question_set=qs2).make()

    qs3 = Recipe(models.QuestionSet, survey=survey, priority=20).make()
    q3 = Recipe(models.Question, question_set=qs3).make()

    with login(client, is_staff=False):
        url = reverse("survey-question-next", args=(session.id, q1.id))
        response = client.get(url)

    new_url = reverse("survey-question-details", args=(session.id, q3.id))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_previous_question_redirects_to_previous_available_question(request, client):
    survey = Recipe(models.Survey, site=get_current_site(request)).make()
    session = Recipe(models.Session, survey=survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    q2 = Recipe(models.Question, question_set=qs).make()

    with login(client, is_staff=False):
        url = reverse("survey-question-previous", args=(session.id, q2.id))
        response = client.get(url)

    new_url = reverse("survey-question-details", args=(session.id, q1.id))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_previous_question_redirects_to_previous_question_set(request, client):
    survey = Recipe(models.Survey, site=get_current_site(request)).make()
    session = Recipe(models.Session, survey=survey).make()
    qs1 = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs1).make()

    qs2 = Recipe(models.QuestionSet, survey=survey).make()
    q2 = Recipe(models.Question, question_set=qs2).make()

    with login(client, is_staff=False):
        url = reverse("survey-question-previous", args=(session.id, q2.id))
        response = client.get(url)

    new_url = reverse("survey-question-details", args=(session.id, q1.id))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_previous_question_redirects_to_survey_when_not_more_questions(request, client):
    survey = Recipe(models.Survey, site=get_current_site(request)).make()
    session = Recipe(models.Session, survey=survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()

    with login(client, is_staff=False):
        url = reverse("survey-question-previous", args=(session.id, q1.id))
        response = client.get(url)

    new_url = reverse("survey-session-details", args=(session.id,))
    assertRedirects(response, new_url)


########################################################################
# Signals refresh
########################################################################


@pytest.mark.django_db
def test_refresh_signals_only_for_staff(request, client):
    current_site = get_current_site(request)
    session = Recipe(models.Session, survey__site=current_site).make()
    url = reverse("survey-session-refresh-signals", args=(session.id,))
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_refresh_signals(request, client):
    survey = Recipe(models.Survey, site=get_current_site(request)).make()
    session = Recipe(models.Session, survey=survey).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()
    choice = Recipe(
        models.Choice, question=q1, value="yep", signals="lima-charlie, bravo-zulu"
    ).make()

    # Answer question first
    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, username="non_site_admin"):
        client.post(url, data={"answer": choice.value})

    # Update choice signal and refresh
    new_signal = "new-signal"
    choice.signals = new_signal
    choice.save()

    url = reverse("survey-session-refresh-signals", args=(session.id,))
    with login(client, groups=["example_com_admin"], username="site_admin"):
        client.get(url)

    # Fetch persisted answer
    answer = models.Answer.objects.get(session=session, question=q1)
    assert answer.signals == "new-signal"


# -- Project reactivation
@pytest.mark.django_db
def test_answered_question_reactivates_inactive_project(request, client, make_project):
    current_site = get_current_site(request)
    project = make_project(site=current_site, inactive_since=timezone.now())

    survey = Recipe(models.Survey, site=current_site).make()
    session = Recipe(models.Session, survey=survey, project=project).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()

    my_comment = "this is a comment"
    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False) as user:
        assign_collaborator(user, project)
        response = client.post(url, data={"comment": my_comment})

    assert response.status_code == 302

    project.refresh_from_db()
    assert project.inactive_since is None


# -- Project activity flags
@pytest.mark.django_db
def test_last_members_activity_is_updated_by_survey_edition_from_member(
    request, client, make_project
):
    current_site = get_current_site(request)
    project = make_project(site=current_site, inactive_since=timezone.now())

    survey = Recipe(models.Survey, site=current_site).make()
    session = Recipe(models.Session, survey=survey, project=project).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()

    my_comment = "this is a comment"
    url = reverse("survey-question-details", args=(session.id, q1.id))

    before_update = timezone.now()

    with login(client, is_staff=False) as user:
        assign_collaborator(user, project)
        response = client.post(url, data={"comment": my_comment})

    assert response.status_code == 302

    project.refresh_from_db()
    assert project.last_members_activity_at > before_update


@pytest.mark.django_db
def test_last_members_activity_not_updated_by_survey_edition_from_advisor(
    request, client
):
    current_site = get_current_site(request)

    project_ts = timezone.now()
    project = Recipe(
        projects.Project,
        sites=[current_site],
        inactive_since=timezone.now(),
        last_members_activity_at=project_ts,
    ).make()
    survey = Recipe(models.Survey, site=current_site).make()
    session = Recipe(models.Session, survey=survey, project=project).make()

    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()

    my_comment = "this is a comment"
    url = reverse("survey-question-details", args=(session.id, q1.id))

    with login(client, is_staff=False) as user:
        assign_advisor(user, project)
        response = client.post(url, data={"comment": my_comment})

    assert response.status_code == 302

    project.refresh_from_db()
    assert project.last_members_activity_at == project_ts


# eof
