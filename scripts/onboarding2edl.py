from recoco.apps.home.models import SiteConfiguration
from recoco.apps.survey.models import (
    Answer,
    Choice,
    Question,
    QuestionSet,
    Session,
)


def run():
    for sc in SiteConfiguration.objects.all():
        print(f"\n************ {sc.site} ************\n\n")
        onboarding = sc.onboarding

        # Create question set
        qset, _created = QuestionSet.objects.get_or_create(
            survey=sc.project_survey,
            heading="Contexte de la demande",
            priority=10000,
            icon="arrow-down-square",
        )

        # Create questions
        for idx, element in enumerate(onboarding.form):
            comment_title = ""
            if "placeholder" in element:
                comment_title = element["placeholder"]

            if element["type"] in ("text", "textarea"):
                print(f"Creating TEXT question {element['label']}")
                question, _ = Question.objects.get_or_create(
                    question_set=qset,
                    text=element["label"],
                    text_short=element["label"][:28],
                    priority=100 - idx,
                    comment_title=comment_title,
                )

            elif element["type"] == "checkbox-group":
                try:
                    text = element["values"][0]["label"]
                except KeyError:
                    text = element["label"]

                print(f"Creating YES/NO question {text}")
                question, _ = Question.objects.get_or_create(
                    is_multiple=False,
                    question_set=qset,
                    text=text,
                    text_short=element["label"][:28],
                    priority=100 - idx,
                    comment_title=comment_title,
                )

                Choice.objects.get_or_create(
                    question=question, text="Oui", value="yes", priority=1
                )
                Choice.objects.get_or_create(
                    question=question, text="Non", value="no", priority=0
                )
            else:
                print(f"Ignoring form entry of type {element['type']}")

            sc.onboarding_questions.add(question)

        print("============== ANSWERS ==================")
        for onb_resp in onboarding.responses.all():
            session = Session.objects.filter(
                project=onb_resp.project, survey=sc.project_survey
            ).first()
            if not session:
                continue

            # Create answer and match per label
            for label, answer in onb_resp.response.items():
                if not label:
                    continue
                q = Question.objects.filter(
                    question_set__survey__sessions__project=onb_resp.project,
                    text=label,
                ).first()
                if not q:
                    q = Question.objects.filter(
                        question_set__survey__sessions__project=onb_resp.project,
                        text_short=label,
                    ).first()
                if not q:
                    print(f"Couldn't find matching question for {label}")
                    continue

                if q.choices.count() == 0:  # simple answer
                    print(f"Creating answer for {q} : {answer}")
                    Answer.objects.get_or_create(
                        question=q,
                        session=session,
                        comment=answer,
                    )
                else:
                    if len(answer):
                        choice = Choice.objects.get(question=q, value="yes")
                    else:
                        choice = Choice.objects.get(question=q, value="no")
                    a, a_created = Answer.objects.get_or_create(
                        question=q,
                        session=session,
                    )
                    if a_created:
                        a.choices.add(choice)
                        a.values = [choice.value]
                        a.save()
