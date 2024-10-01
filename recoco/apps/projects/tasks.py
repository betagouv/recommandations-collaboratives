from celery import shared_task

from .models import Project


@shared_task()
def collect_survey_answers_in_project(project_id: int):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return

    session = project.survey_session.last()
    if not session:
        return

    project.survey_answers.update(
        {
            answer.question.slug: answer.as_dict
            for answer in session.answers.all().select_related("question")
        }
    )
    project.save()
