# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods

from recoco.apps.addressbook.models import Contact
from recoco.apps.projects import models as project_models
from recoco.apps.projects.forms import DocumentUploadForm
from recoco.apps.projects.utils import (
    can_administrate_project,
    get_collaborators_for_project,
)
from recoco.apps.survey import models as survey_models
from recoco.utils import check_if_advisor, has_perm_or_403, is_staff_for_site_or_403

from .. import models, signals
from ..forms import (
    CreateActionWithResourceForm,
    CreateActionWithoutResourceForm,
    PushTypeActionForm,
    RsvpTaskFollowupForm,
    TaskFollowupForm,
    TaskRecommendationForm,
    UpdateTaskFollowupForm,
    UpdateTaskForm,
)

########################################################################
# create task/push resource to project
########################################################################


@login_required
def create_task(request):
    """Create task"""

    is_switchtender = check_if_advisor(request.user)
    if not (
        is_switchtender or can_administrate_project(project=None, user=request.user)
    ):
        return HttpResponseForbidden()

    if request.method == "POST":
        # Pick a different form for better data handling based
        # on the 'push_type' attribute
        type_form = PushTypeActionForm(user=request.user, data=request.POST)

        type_form.is_valid()

        push_type = type_form.cleaned_data.get("push_type")

        try:
            push_form_type = {
                "single": CreateActionWithResourceForm,
                "external_resource": CreateActionWithResourceForm,
                "noresource": CreateActionWithoutResourceForm,
            }[push_type]
        except KeyError:
            return render(request, "tasks/tasks/task_create.html", locals())

        form = push_form_type(request.POST)
        if form.is_valid():
            project = type_form.cleaned_data.get("project")
            contact = type_form.cleaned_data.get("contact")

            has_perm_or_403(request.user, "projects.manage_tasks", project)

            action = form.save(commit=False)
            action.project = project
            action.site = request.site
            action.created_by = request.user
            if contact:
                action.contact = contact

            # get or create topic
            name = form.cleaned_data["topic_name"]
            if name:
                topic, _ = project_models.Topic.objects.get_or_create(
                    name__iexact=name.lower(),
                    defaults={"name": name.capitalize(), "site": request.site},
                )
                action.topic = topic
            action.save()

            # Depending on wether we already have a recommandation on the same day:
            # - move the new action after the existing one on the same day
            # - let it on top if the following one was at least yesterday
            today = datetime.date.today()
            previous_today_action = (
                models.Task.objects.filter(project=action.project)
                .exclude(id=action.id)
                .filter(created_on__date=today)
                .order_by("-created_on")
                .first()
            )
            if previous_today_action:
                action.below(previous_today_action)
            else:
                action.top()

            # Check if we have a file or link
            document_form = DocumentUploadForm(request.POST, request.FILES)
            if document_form.is_valid():
                if document_form.cleaned_data["the_file"]:
                    document = document_form.save(commit=False)
                    document.attached_object = action
                    document.site = request.site
                    document.uploaded_by = request.user
                    document.project = action.project
                    document.save()

            # Notify other switchtenders
            signals.action_created.send(
                sender=create_task,
                task=action,
                project=project,
                user=request.user,
            )

            # Redirect to `action-inline` if we're coming
            # from `action-inline` after create
            if (
                type_form.cleaned_data["next"]
                and type_form.cleaned_data["next"] != "None"
            ):
                return redirect(type_form.cleaned_data["next"])

            next_url = reverse("projects-project-detail-actions", args=[project.id])
            return redirect(next_url)
    else:
        type_form = PushTypeActionForm(request.user, request.GET)
        # Get preserved content from URL parameter
        preserved_content = request.GET.get("content", "")

    return render(request, "tasks/tasks/task_create.html", locals())


@login_required
def visit_task(request, task_id):
    """Visit the content of a task"""
    task = get_object_or_404(models.Task, site=request.site, pk=task_id)

    has_perm_or_403(request.user, "projects.view_tasks", task.project)

    is_switchtender = check_if_advisor(request.user)

    if not task.visited and not is_switchtender and not request.user.is_hijacked:
        task.visited = True
        task.save()

        signals.action_visited.send(
            sender=visit_task, task=task, project=task.project, user=request.user
        )

    if task.resource:
        return redirect(reverse("resources-resource-detail", args=[task.resource.pk]))

    return redirect(reverse("projects-project-detail-actions", args=[task.project_id]))


@login_required
def toggle_done_task(request, task_id):
    """Mark task as done for a project"""
    task = get_object_or_404(models.Task, site=request.site, pk=task_id)

    has_perm_or_403(request.user, "projects.use_tasks", task.project)

    if request.method == "POST":
        if task.open:
            task.status = models.Task.DONE

            signals.action_done.send(
                sender=toggle_done_task,
                task=task,
                project=task.project,
                user=request.user,
            )
        else:
            task.status = models.Task.PROPOSED

            signals.action_undone.send(
                sender=toggle_done_task,
                task=task,
                project=task.project,
                user=request.user,
            )
        task.save()

    return redirect(reverse("projects-project-detail-actions", args=[task.project_id]))


@login_required
def refuse_task(request, task_id):
    """Mark task refused for a project (user not interested)"""
    task = get_object_or_404(models.Task, site=request.site, pk=task_id)

    has_perm_or_403(request.user, "projects.use_tasks", task.project)

    if request.method == "POST":
        task.status = models.Task.NOT_INTERESTED
        task.save()
        signals.action_not_interested.send(
            sender=refuse_task, task=task, project=task.project, user=request.user
        )

    return redirect(reverse("projects-project-detail-actions", args=[task.project_id]))


@login_required
def already_done_task(request, task_id):
    """Mark task refused for a project"""
    task = get_object_or_404(models.Task, site=request.site, pk=task_id)

    has_perm_or_403(request.user, "projects.use_tasks", task.project)

    if request.method == "POST":
        task.status = models.Task.ALREADY_DONE
        task.save()
        signals.action_already_done.send(
            sender=already_done_task, task=task, project=task.project, user=request.user
        )

    return redirect(reverse("projects-project-detail-actions", args=[task.project_id]))


@login_required
def sort_task(request, task_id, order):
    """Update an existing task for a project"""
    task = get_object_or_404(models.Task, site=request.site, pk=task_id)

    has_perm_or_403(request.user, "projects.use_tasks", task.project)

    if order == "up":
        task.up()
    elif order == "down":
        task.down()
    else:
        return HttpResponseForbidden()

    task.save()

    return redirect(
        reverse("projects-project-detail-actions", args=[task.project_id])
        + f"#action-{task.id}"
    )


@login_required
def update_task(request, task_id=None):
    """Update an existing task for a project"""
    task = get_object_or_404(models.Task, site=request.site, pk=task_id)

    has_perm_or_403(request.user, "projects.manage_tasks", task.project)

    was_public = task.public

    if request.method == "POST":
        form = UpdateTaskForm(request.POST, instance=task)
        form.set_contact_queryset(
            Contact.objects.filter(site_id=request.site.id),
        )
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_on = timezone.now()
            # manage topic
            name = form.cleaned_data["topic_name"]

            if name:
                topic, _ = project_models.Topic.objects.get_or_create(
                    name__iexact=name.lower(),
                    defaults={"name": name.capitalize(), "site": request.site},
                )
                instance.topic = topic
            instance.save()
            instance.project.updated_on = instance.updated_on
            instance.project.save()

            document_form = DocumentUploadForm(request.POST, request.FILES)
            if document_form.is_valid():
                if document_form.cleaned_data["the_file"]:
                    document = document_form.save(commit=False)
                    document.attached_object = instance
                    document.site = request.site
                    document.uploaded_by = request.user
                    document.project = instance.project
                    document.save()

            # If we are going public, notify
            if was_public is False and instance.public is True:
                signals.action_created.send(
                    sender=update_task,
                    task=instance,
                    project=instance.project,
                    user=request.user,
                )

            # Redirect to `action-inline` if we're coming
            # from `action-inline` after create
            if form.cleaned_data["next"] and form.cleaned_data["next"] != "None":
                return redirect(form.cleaned_data["next"])

            return redirect(
                reverse("projects-project-detail-actions", args=[task.project_id])
            )
    else:
        initial = {
            "topic_name": task.topic.name if task.topic else None,
            "next": request.GET.get("next"),
        }
        form = UpdateTaskForm(instance=task, initial=initial)
        document_form = DocumentUploadForm()
    return render(request, "tasks/tasks/task_update.html", locals())


########
# Task Recommendation
########


# liste de preflechage des recommendations
@login_required
def task_recommendation_list(request):
    """List task recommendations for a project"""
    is_staff_for_site_or_403(request.user)

    recommendations = (
        models.TaskRecommendation.on_site.all()
        .select_related("resource__category")
        .prefetch_related("departments")
    )

    return render(request, "tasks/tasks/recommendation_list.html", locals())


# ajout d'un  preflechage de recommendations
@login_required
def task_recommendation_create(request):
    """Create a new task recommendation for a project"""
    is_staff_for_site_or_403(request.user)

    if request.method == "POST":
        form = TaskRecommendationForm(request.POST)
        if form.is_valid():
            reco = form.save(commit=False)
            reco.site = request.site
            reco.save()

            return redirect(reverse("projects-task-recommendation-list"))
    else:
        form = TaskRecommendationForm()
    return render(request, "tasks/tasks/recommendation_create.html", locals())


# mise à jour d'un  preflechage de recommendations
@login_required
def task_recommendation_update(request, recommendation_id):
    """Update a task recommendation"""

    is_staff_for_site_or_403(request.user)

    recommendation = get_object_or_404(
        models.TaskRecommendation, site=request.site, pk=recommendation_id
    )

    if request.method == "POST":
        form = TaskRecommendationForm(request.POST, instance=recommendation)
        if form.is_valid():
            form.save()
            return redirect(reverse("projects-task-recommendation-list"))
    else:
        form = TaskRecommendationForm(instance=recommendation)

    return render(request, "tasks/tasks/recommendation_update.html", locals())


@login_required
@require_http_methods(["POST"])
def task_recommendation_delete(request, recommendation_id):
    """Delete a task recommendation"""

    is_staff_for_site_or_403(request.user)

    task_recommendation = get_object_or_404(
        models.TaskRecommendation, site=request.site, pk=recommendation_id
    )
    task_recommendation.delete()

    messages.success(
        request=request,
        message="Le pré-fléchage a bien été supprimé",
    )

    return redirect(reverse("projects-task-recommendation-list"))


# retourne pour le dossier les suggestions du système
@login_required
def presuggest_task(request, project_id):
    """Suggest tasks"""
    project = get_object_or_404(
        project_models.Project, sites=request.site, pk=project_id
    )

    has_perm_or_403(request.user, "projects.manage_tasks", project)

    signals = set()

    # Get signals from survey session
    if request.site.configuration.project_survey:
        try:
            survey = survey_models.Survey.on_site.get(
                pk=request.site.configuration.project_survey.pk
            )
        except survey_models.Survey.DoesNotExist:
            survey = None

        if survey:
            session, _ = survey_models.Session.objects.get_or_create(
                project=project, survey=survey
            )

            signals = signals.union(session.signals)

    tasks = []

    # Make signals from project topics
    project_signals = set()
    for topic in project.topics.all():
        project_signals.add(f"project_topic:{slugify(topic.name)}")

    signals = signals.union(project_signals)

    # Now, find matching TaskRecommendation
    for recommandation in models.TaskRecommendation.on_site.all():
        if not project.commune:
            continue

        if recommandation.departments.all().count() > 0:
            if (
                project.commune.department.code
                not in recommandation.departments.values_list("code", flat=True)
            ):
                continue

        reco_tags = set(recommandation.condition_tags.values_list("name", flat=True))
        if reco_tags.issubset(signals):
            tasks.append(
                models.Task(
                    id=0,
                    project=project,
                    resource=recommandation.resource,
                    intent=recommandation.text,
                )
            )

    return render(request, "tasks/tasks/task_suggest.html", locals())


@login_required
def delete_task(request, task_id=None):
    """Delete a task from a project"""
    task = get_object_or_404(models.Task, site=request.site, pk=task_id)
    has_perm_or_403(request.user, "projects.manage_tasks", task.project)

    if request.method == "POST":
        task.deleted = timezone.now()
        task.save()

    next_url = reverse("projects-project-detail-actions", args=[task.project_id])
    return redirect(next_url)


@login_required
def followup_task(request, task_id=None):
    """Create a new followup for task"""
    task = get_object_or_404(models.Task, site=request.site, pk=task_id)

    has_perm_or_403(request.user, "projects.use_tasks", task.project)

    if request.method == "POST":
        form = TaskFollowupForm(request.POST)
        if form.is_valid():
            followup = form.save(commit=False)
            followup.task = task
            followup.who = request.user

            followup.save()

            # update activity flags and states
            if request.user in get_collaborators_for_project(task.project):
                task.project.last_members_activity_at = timezone.now()

                if task.project.inactive_since:
                    task.project.reactivate()

                task.project.save()

    return redirect(reverse("projects-project-detail-actions", args=[task.project.id]))


@login_required
def followup_task_update(request, followup_id=None):
    """Update a followup for task"""
    followup = get_object_or_404(
        models.TaskFollowup, task__site=request.site, pk=followup_id
    )

    if followup.who != request.user:
        return HttpResponseForbidden()

    form = UpdateTaskFollowupForm(
        request.POST or request.GET or None, instance=followup
    )
    if request.method == "POST":
        if form.is_valid():
            followup = form.save()

            return redirect(
                reverse(
                    "projects-project-detail-actions", args=[followup.task.project.id]
                )
                + f"#action-{followup.task.id}"
            )
    return render(request, "tasks/task/task_followup_update.html", locals())


def rsvp_followup_task(request, rsvp_id=None, status=None):
    """Manage the user task followup from her rsvp email.
    Triggered when a user clicks on a rsvp link
    """
    try:
        rsvp = models.TaskFollowupRsvp.objects.get(uuid=rsvp_id)
    except models.TaskFollowupRsvp.DoesNotExist:
        return render(request, "tasks/task/rsvp_followup_invalid.html", locals())

    task = rsvp.task

    rsvp_signals = [
        models.Task.INPROGRESS,
        models.Task.DONE,
        models.Task.ALREADY_DONE,
        models.Task.NOT_INTERESTED,
        models.Task.BLOCKED,
    ]

    if status not in rsvp_signals:
        raise Http404()

    if request.method == "POST":
        form = RsvpTaskFollowupForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data.get("comment", "")
            followup = models.TaskFollowup(
                status=status, comment=comment, task=task, who=rsvp.user
            )
            followup.save()

            rsvp.delete()  # we are done with this use only once object

            return render(request, "tasks/task/rsvp_followup_thanks.html", locals())
    else:
        form = RsvpTaskFollowupForm()
    return render(request, "tasks/task/rsvp_followup_confirm.html", locals())
