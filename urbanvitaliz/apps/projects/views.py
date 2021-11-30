# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from django import forms
from django.contrib import messages
from django.contrib.auth import login as log_user
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.contrib.syndication.views import Feed
from django.dispatch import receiver
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from markdownx.fields import MarkdownxFormField
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.reminders import api
from urbanvitaliz.apps.resources import models as resources
from urbanvitaliz.apps.survey import models as survey_models
from urbanvitaliz.utils import (
    check_if_switchtender,
    is_staff_or_403,
    is_switchtender_or_403,
    send_email,
)

from . import models, signals
from .utils import (
    can_administrate_or_403,
    can_administrate_project,
    generate_ro_key,
    get_active_project,
    get_active_project_id,
    refresh_user_projects_in_session,
    set_active_project_id,
)

########################################################################
# notifications
########################################################################


def notify_action_created(request, project, task, resource=None):
    """
    Notify the creation of an Action the user by sending an email and displaying
    a UI popup
    """
    # TODO send to all project emails
    send_email(
        request,
        user_email=project.email,
        email_subject="[{0}] UrbanVitaliz vous propose une action".format(project.name),
        template_base_name="projects/notifications/task_new_email",
        extra_context={
            "task": task,
            "project": project,
            "resource": resource,
        },
    )

    messages.success(
        request,
        '{0} a été notifié(e) par courriel de l\'action "{1}".'.format(
            project.full_name, task.intent
        ),
        extra_tags=["email"],
    )


########################################################################
# On boarding
########################################################################


def onboarding(request):
    """Return the onboarding page"""
    if request.method == "POST":
        form = OnboardingForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.emails.append(project.email)
            project.ro_key = generate_ro_key()
            postcode = form.cleaned_data.get("postcode")
            project.commune = geomatics.Commune.get_by_postal_code(postcode)
            # concatener les impediment_kinds et la rajouter en debut d'impediment
            impediment_kinds = form.cleaned_data.get("impediment_kinds", [])
            project.impediments = (
                "#### Besoins : "
                + " ; ".join(impediment_kinds)
                + "\n\n"
                + project.impediments
            )
            project.save()
            models.Note(
                project=project,
                content=f"# Demande initiale\n\n{project.impediments}",
                public=True,
            ).save()

            signals.project_submitted.send(sender=models.Project, project=project)

            # TODO get or create user and log her in the application
            user, _ = auth.User.objects.get_or_create(
                username=project.email,
                defaults={
                    "email": project.email,
                },
            )
            log_user(request, user)

            response = redirect("survey-project-session", project_id=project.id)
            response["Location"] += "?first_time=1"
            return response
    else:
        form = OnboardingForm()
    return render(request, "projects/onboarding.html", locals())


class OnboardingForm(forms.ModelForm):
    """Form for onboarding a new local authority"""

    postcode = forms.CharField(max_length=5, required=False, label="Code Postal")

    impediment_kinds = forms.MultipleChoiceField(
        choices=[
            (
                "Méthode à suivre, guidage sur les prochaines étapes et questions à se poser",
                "Méthode à suivre, guidage sur les prochaines étapes et questions à se poser",
            ),
            (
                "Définition du projet de réhabilitation",
                "Définition du projet de réhabilitation",
            ),
            (
                "Accompagnement, conseil et compétences techniques avant travaux",
                "Accompagnement, conseil et compétences techniques avant travaux",
            ),
            ("Financement pour des études", "Financement pour des études"),
            ("Financement des travaux", "Financement des travaux"),
            (
                "Propriété de la friche, acquisition, contact avec le propriétaire",
                "Propriété de la friche, acquisition, contact avec le propriétaire",
            ),
            ("Autre", "Autre (précisez en commentaire)"),
        ],
        required=True,
        label="Quels sont les besoins et points de blocage?",
    )

    class Meta:
        model = models.Project
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "org_name",
            "name",
            "location",
            "description",
            "impediments",
            "publish_to_cartofriches",
        ]


########################################################################
# Switchtender
########################################################################


@login_required
def project_list(request):
    """Return the projects for the switchtender"""
    is_switchtender_or_403(request.user)
    projects = models.Project.objects.in_departments(
        request.user.profile.departments.all()
    ).order_by("-created_on")
    return render(request, "projects/project/list.html", locals())


@login_required
def project_detail(request, project_id=None):
    """Return the details of given project for switchtender"""
    project = get_object_or_404(models.Project, pk=project_id)

    # check user can administrate projet (member or switchtender)
    if request.user.email != project.email:
        can_administrate_or_403(project, request.user)

    # Set this project as active
    set_active_project_id(request, project.pk)

    try:
        survey = survey_models.Survey.objects.get(pk=1)  # XXX Hardcoded survey ID
        session, created = survey_models.Session.objects.get_or_create(
            project=project, survey=survey
        )
    except survey_models.Survey.DoesNotExist:
        session = None

    can_administrate = can_administrate_project(project, request.user)
    can_administrate_draft = can_administrate_project(
        project, request.user, allow_draft=True
    )

    return render(request, "projects/project/detail.html", locals())


def project_detail_from_sharing_link(request, project_ro_key):
    """Return a special view of the project using the sharing link"""
    try:
        project = models.Project.objects.filter(ro_key=project_ro_key)[0]
    except Exception:
        raise Http404()

    can_administrate = can_administrate_project(project, request.user)

    return render(request, "projects/project/detail-ro.html", locals())


@login_required
def project_update(request, project_id=None):
    """Update the base information of a project"""
    is_switchtender_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            instance = form.save(commit=False)
            postcode = form.cleaned_data.get("postcode")
            project.commune = geomatics.Commune.get_by_postal_code(postcode)
            instance.updated_on = timezone.now()
            instance.save()
            return redirect(reverse("projects-project-detail", args=[project_id]))
    else:
        if project.commune:
            postcode = project.commune.postal
        else:
            postcode = None
        form = ProjectForm(instance=project, initial={"postcode": postcode})
    return render(request, "projects/project/update.html", locals())


@login_required
def project_accept(request, project_id=None):
    """Update project as accepted for processing"""
    is_switchtender_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        project.is_draft = False
        project.updated_on = timezone.now()
        project.save()
    return redirect(reverse("projects-project-detail", args=[project_id]))


@login_required
def project_delete(request, project_id=None):
    """Mark project as deleted in the DB"""
    is_staff_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        project.deleted = project.updated_on = timezone.now()
        project.save()
    return redirect(reverse("projects-project-list"))


class ProjectForm(forms.ModelForm):
    """Form for updating the base information of a project"""

    postcode = forms.CharField(max_length=5, required=False, label="Code Postal")
    publish_to_cartofriches = forms.BooleanField(
        label="Publication sur cartofriches", disabled=True, required=False
    )

    class Meta:
        model = models.Project
        fields = [
            "email",
            "first_name",
            "last_name",
            "org_name",
            "phone",
            "name",
            "postcode",
            "location",
            "description",
            "switchtender",
            "publish_to_cartofriches",
        ]


@login_required
def create_note(request, project_id=None):
    """Create a new note for a project"""
    project = get_object_or_404(models.Project, pk=project_id)
    can_administrate_or_403(project, request.user, allow_draft=True)
    is_switchtender = check_if_switchtender(request.user)

    if request.method == "POST":
        if is_switchtender:
            form = StaffNoteForm(request.POST)
        else:
            form = NoteForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.project = project
            if not is_switchtender:
                instance.public = True
            instance.save()
            return redirect(
                reverse("projects-project-detail", args=[project_id]) + "#sheet"
            )
    else:
        if is_switchtender:
            form = StaffNoteForm()
        else:
            form = NoteForm()
    return render(request, "projects/project/note_create.html", locals())


@login_required
def update_note(request, note_id=None):
    """Update an existing note for a project"""
    note = get_object_or_404(models.Note, pk=note_id)
    project = note.project  # For template consistency
    can_administrate_or_403(project, request.user, allow_draft=True)
    is_switchtender = check_if_switchtender(request.user)

    if not note.public:
        is_switchtender_or_403(request.user)

    if request.method == "POST":
        if is_switchtender:
            form = StaffNoteForm(request.POST, instance=note)
        else:
            form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_on = timezone.now()
            instance.save()
            instance.project.updated_on = instance.updated_on
            instance.project.save()
            return redirect(
                reverse("projects-project-detail", args=[note.project_id]) + "#sheet"
            )
    else:
        if is_switchtender:
            form = StaffNoteForm(instance=note)
        else:
            form = NoteForm(instance=note)
    return render(request, "projects/project/note_update.html", locals())


@login_required
def delete_note(request, note_id=None):
    """Delete existing note for a project"""
    is_switchtender_or_403(request.user)
    note = get_object_or_404(models.Note, pk=note_id)

    if request.method == "POST":
        note.updated_on = timezone.now()
        note.deleted = timezone.now()
        note.save()
        note.project.updated_on = note.updated_on
        note.project.save()

    return redirect(reverse("projects-project-detail", args=[note.project_id]))


class NoteForm(forms.ModelForm):
    """Form new project note creation"""

    class Meta:
        model = models.Note
        fields = ["content", "tags"]

    content = MarkdownxFormField()


class StaffNoteForm(NoteForm):
    class Meta:
        model = models.Note
        fields = ["content", "tags", "public"]


@login_required
def create_task(request, project_id=None):
    """Create a new task for a project"""
    is_switchtender_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.project = project
            instance.save()

            if not project.switchtender:
                project.switchtender = request.user
                project.save()

            # Send notifications
            if form.cleaned_data["notify_email"]:
                notify_action_created(request, project, task=instance)

            return redirect(reverse("projects-project-detail", args=[project_id]))
    else:
        form = CreateTaskForm()
    return render(request, "projects/project/task_create.html", locals())


@login_required
def visit_task(request, task_id):
    """Visit the content of a task"""
    task = get_object_or_404(models.Task, pk=task_id)
    can_administrate_or_403(task.project, request.user, allow_draft=True)
    is_switchtender = check_if_switchtender(request.user)

    if not task.visited and not is_switchtender:
        task.visited = True
        task.save()

        signals.action_visited.send(
            sender=visit_task, task=task, project=task.project, user=request.user
        )

    if task.resource:
        return redirect(reverse("resources-resource-detail", args=[task.resource.pk]))

    return redirect(
        reverse("projects-project-detail", args=[task.project_id]) + "#actions"
    )


@login_required
def toggle_done_task(request, task_id):
    """Mark task as done for a project"""
    task = get_object_or_404(models.Task, pk=task_id)
    can_administrate_or_403(task.project, request.user)

    if request.method == "POST":
        task.refused = False
        task.done = not task.done
        if task.done:
            # NOTE should we remove all the reminders?
            api.remove_reminder_email(
                task, recipient=request.user.email, origin=api.models.Mail.STAFF
            )
            signals.action_done.send(
                sender=toggle_done_task,
                task=task,
                project=task.project,
                user=request.user,
            )
        else:
            signals.action_undone.send(
                sender=toggle_done_task,
                task=task,
                project=task.project,
                user=request.user,
            )
        task.save()

    return redirect(
        reverse("projects-project-detail", args=[task.project_id]) + "#actions"
    )


@login_required
def refuse_task(request, task_id):
    """Mark task refused for a project"""
    task = get_object_or_404(models.Task, pk=task_id)
    can_administrate_or_403(task.project, request.user)

    if request.method == "POST":
        task.done = False
        task.refused = True
        task.save()
        api.remove_reminder_email(task)
        signals.action_rejected.send(
            sender=refuse_task, task=task, project=task.project, user=request.user
        )

    return redirect(
        reverse("projects-project-detail", args=[task.project_id]) + "#actions"
    )


@login_required
def already_done_task(request, task_id):
    """Mark task refused for a project"""
    task = get_object_or_404(models.Task, pk=task_id)
    can_administrate_or_403(task.project, request.user)

    if request.method == "POST":
        task.done = True
        task.refused = True
        task.save()
        api.remove_reminder_email(
            task, recipient=request.user.email, origin=api.models.Mail.STAFF
        )
        signals.action_already_done.send(
            sender=already_done_task, task=task, project=task.project, user=request.user
        )

    return redirect(
        reverse("projects-project-detail", args=[task.project_id]) + "#actions"
    )


@login_required
def update_task(request, task_id=None):
    """Update an existing task for a project"""
    is_switchtender_or_403(request.user)
    task = get_object_or_404(models.Task, pk=task_id)
    if request.method == "POST":
        form = UpdateTaskForm(request.POST, instance=task)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_on = timezone.now()
            instance.save()
            instance.project.updated_on = instance.updated_on
            instance.project.save()
            api.remove_reminder_email(
                task, recipient=request.user.email, origin=api.models.Mail.STAFF
            )
            return redirect(reverse("projects-project-detail", args=[task.project_id]))
    else:
        form = UpdateTaskForm(instance=task)
    return render(request, "projects/project/task_update.html", locals())


########
# Task Recommendation
########


class TaskRecommendationForm(forms.ModelForm):
    """Form new task recommendation creation"""

    class Meta:
        model = models.TaskRecommendation
        fields = ["condition", "resource", "text", "departments"]


@login_required
def task_recommendation_create(request):
    """Create a new task recommendation for a project"""
    is_staff_or_403(request.user)

    if request.method == "POST":
        form = TaskRecommendationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("projects-task-recommendation-list"))
    else:
        form = TaskRecommendationForm()
    return render(request, "projects/tasks/recommendation_create.html", locals())


@login_required
def task_recommendation_update(request, recommendation_id):
    """Update a task recommendation"""
    is_staff_or_403(request.user)

    recommendation = get_object_or_404(models.TaskRecommendation, pk=recommendation_id)

    if request.method == "POST":
        form = TaskRecommendationForm(request.POST, instance=recommendation)
        if form.is_valid():
            form.save()
            return redirect(reverse("projects-task-recommendation-list"))
    else:
        form = TaskRecommendationForm(instance=recommendation)

    return render(request, "projects/tasks/recommendation_update.html", locals())


@login_required
def task_recommendation_list(request):
    """List task recommendations for a project"""
    is_staff_or_403(request.user)

    recommendations = models.TaskRecommendation.objects.all()

    return render(request, "projects/tasks/recommendation_list.html", locals())


@login_required
def presuggest_task(request, project_id):
    """Suggest tasks"""
    is_switchtender_or_403(request.user)

    project = get_object_or_404(models.Project, pk=project_id)

    try:
        survey = survey_models.Survey.objects.get(pk=1)  # XXX Hardcoded survey ID
        session, created = survey_models.Session.objects.get_or_create(
            project=project, survey=survey
        )
    except survey_models.Survey.DoesNotExist:
        session = None

    tasks = []

    if session:
        session_signals = session.signals

        for recommandation in models.TaskRecommendation.objects.all():
            if not project.commune:
                continue

            if recommandation.departments.all().count() > 0:
                if not (
                    project.commune.department.code
                    in recommandation.departments.values_list("code", flat=True)
                ):
                    continue

            reco_tags = set(
                recommandation.condition_tags.values_list("name", flat=True)
            )
            if reco_tags.issubset(session_signals):
                tasks.append(
                    models.Task(
                        id=0,
                        project=project,
                        resource=recommandation.resource,
                        intent=recommandation.text,
                    )
                )

    return render(request, "projects/project/task_suggest.html", locals())


class CreateTaskForm(forms.ModelForm):
    """Form new project task creation"""

    content = MarkdownxFormField(required=False)

    notify_email = forms.BooleanField(initial=False, required=False)

    class Meta:
        model = models.Task
        fields = [
            "intent",
            "content",
            "tags",
            "public",
            "priority",
            "deadline",
            "resource",
            "contact",
            "done",
            "notify_email",
        ]


class UpdateTaskForm(forms.ModelForm):
    """Form for task update"""

    content = MarkdownxFormField(required=False)

    class Meta:
        model = models.Task
        fields = [
            "intent",
            "content",
            "tags",
            "public",
            "priority",
            "deadline",
            "resource",
            "contact",
            "done",
        ]


@login_required
def delete_task(request, task_id=None):
    """Delete a task from a project"""
    is_switchtender_or_403(request.user)
    task = get_object_or_404(models.Task, pk=task_id)
    if request.method == "POST":
        task.deleted = timezone.now()
        task.save()
        api.remove_reminder_email(task)
    next_url = reverse("projects-project-detail", args=[task.project_id])
    return redirect(next_url)


class RemindTaskForm(forms.Form):
    """Remind task after X days"""

    days = forms.IntegerField(min_value=0, required=False, initial=42)


@login_required
def remind_task(request, task_id=None):
    """Set a reminder for a task"""
    task = get_object_or_404(models.Task, pk=task_id)
    recipient = task.project.email

    if request.method == "POST":
        form = RemindTaskForm(request.POST)
        if form.is_valid():
            days = form.cleaned_data.get("days")
            days = days or 6 * 7  # 6 weeks is default

            create_reminder(request, days, task, recipient, origin=api.models.Mail.SELF)

            messages.success(
                request, "Une alarme a bien été programmée dans {0} jours.".format(days)
            )
        else:
            messages.error(request, "Impossible de programmer l'alarme.")

    return redirect(
        reverse("projects-project-detail", args=[task.project_id]) + "#actions"
    )


def create_reminder(request, days, task, recipient, origin):
    subject = f'[UrbanVitaliz] Où en êtes vous suite à nos recommandations pour le site "{task.project.name}"'
    template = "projects/notifications/task_remind_email"
    rsvp, created = models.TaskFollowupRsvp.objects.get_or_create(task=task)
    if not created:
        rsvp.created_on = timezone.now()
        rsvp.save()
    api.create_reminder_email(
        request,
        recipient,
        subject,
        template,
        related=task,
        origin=origin,
        delay=days,
        extra_context={"task": task, "delay": days, "rsvp": rsvp},
    )
    signals.reminder_created.send(
        sender=models.Project, task=task, project=task.project, user=request.user
    )


@login_required
def followup_task(request, task_id=None):
    """Create a new followup for task"""
    task = get_object_or_404(models.Task, pk=task_id)
    can_administrate_or_403(task.project, request.user)
    if request.method == "POST":
        form = TaskFollowupForm(request.POST)
        if form.is_valid():
            followup = form.save(commit=False)
            followup.task = task
            followup.who = request.user
            # followup.status = task.status
            followup.status = 0
            followup.save()
            signals.action_commented.send(
                sender=followup_task, task=task, project=task.project, user=request.user
            )
    next_url = reverse("projects-project-detail", args=[task.project.id])
    return redirect(next_url + "#actions")


class TaskFollowupForm(forms.ModelForm):
    """Create a new followup for a task"""

    class Meta:
        model = models.TaskFollowup
        fields = ["comment"]


def rsvp_followup_task(request, rsvp_id=None, status=None):
    """Manage the user task followup from her rsvp email."""
    try:
        rsvp = models.TaskFollowupRsvp.objects.get(uuid=rsvp_id)
    except models.TaskFollowupRsvp.DoesNotExist:
        return render(request, "projects/task/rsvp_followup_invalid.html", locals())
    task = rsvp.task
    if status not in [1, 2, 3, 4]:
        raise Http404()
    if request.method == "POST":
        form = RsvpTaskFollowupForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data.get("comment", "")
            models.TaskFollowup(
                status=status, comment=comment, task=task, who=request.user
            ).save()
            rsvp.delete()  # we are done with this use only once object
            # TODO
            # task.status = status
            # task.save()
            return render(request, "projects/task/rsvp_followup_thanks.html", locals())
    else:
        form = RsvpTaskFollowupForm()
    return render(request, "projects/task/rsvp_followup_confirm.html", locals())


class RsvpTaskFollowupForm(forms.Form):

    comment = forms.CharField(widget=forms.Textarea, required=False)


########################################################################
# push resource to project
########################################################################


@login_required
def create_resource_action(request, resource_id=None):
    """Create action for given resource to project stored in session"""
    is_switchtender_or_403(request.user)
    project_id = get_active_project_id(request)
    resource = get_object_or_404(resources.Resource, pk=resource_id)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        form = ResourceTaskForm(request.POST)
        if form.is_valid():
            # create a new bookmark with provided information
            task = form.save(commit=False)
            task.project = project
            task.resource = resource
            task.created_by = request.user
            task.save()

            # Assign switchtender if none yet
            if not project.switchtender:
                project.switchtender = request.user
                project.save()

            # assign reminder in six weeks
            create_reminder(
                request, 6 * 7, task, project.email, origin=api.models.Mail.STAFF
            )

            # Send notifications
            if form.cleaned_data["notify_email"]:
                notify_action_created(request, project, task, resource)

            next_url = reverse("projects-project-detail", args=[project.id])
            return redirect(next_url)
    else:
        form = ResourceTaskForm()
    return render(request, "projects/project/push.html", locals())


class ResourceTaskForm(forms.ModelForm):
    """Create and task for push resource"""

    notify_email = forms.BooleanField(initial=False, required=False)

    class Meta:
        model = models.Task
        fields = ["intent", "content", "contact", "notify_email"]


########################################################################
# Access
########################################################################
class AccessAddForm(forms.Form):
    """A form to add an Access"""

    email = forms.EmailField()


@login_required
def access_update(request, project_id):
    """Handle ACL for a project"""
    project = get_object_or_404(models.Project, pk=project_id)

    can_administrate_or_403(project, request.user)

    if request.method == "POST":
        form = AccessAddForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            if email not in project.emails:
                project.emails.append(email)
                project.save()
                messages.success(
                    request,
                    "Un courriel d'invitation à rejoindre le projet a été envoyé à {0}.".format(
                        email
                    ),
                    extra_tags=["email"],
                )
                send_email(
                    request,
                    user_email=email,
                    email_subject="[UrbanVitaliz] Vous êtes invité·e à collaborer sur {0}".format(
                        project.name
                    ),
                    template_base_name="projects/notifications/acl_new_collaborator",
                    extra_context={"project": project, "email": email},
                )

            return redirect(reverse("projects-project-detail", args=[project_id]))
    else:
        form = AccessAddForm()
    return render(request, "projects/project/access_update.html", locals())


@login_required
def access_delete(request, project_id: int, email: str):
    """Delete en email from the project ACL"""
    project = get_object_or_404(models.Project, pk=project_id)

    can_administrate_or_403(project, request.user)

    if request.method == "POST":
        if email == project.email:
            messages.error(
                request,
                "Vous ne pouvez pas retirer le propriétaire de son propre projet.",
                extra_tags=["auth"],
            )

        elif email in project.emails:
            project.emails.remove(email)
            project.save()
            messages.success(
                request,
                "{0} a bien été supprimé de la liste des collaborateurs.".format(email),
                extra_tags=["auth"],
            )

    return redirect(reverse("projects-access-update", args=[project_id]))


########################################################################
# Login methods and signals
########################################################################
@receiver(user_logged_in)
def post_login_set_active_project(sender, user, request, **kwargs):
    # store my projects in the session
    refresh_user_projects_in_session(request, user)

    active_project = get_active_project(request)

    if not active_project:
        # Try to fetch a project
        active_project = models.Project.objects.filter(email=user.email).first()
        if active_project:
            set_active_project_id(request, active_project.id)


@login_required
def redirect_user_to_project(request):
    """Redirect user to project page given her context"""
    active_project = get_active_project(request)

    if active_project:
        return redirect(reverse("projects-project-detail", args=[active_project.id]))
    else:
        return redirect(reverse("home"))


########################################################################
# RSS Feeds
########################################################################


class LatestProjectsFeed(Feed):
    title = "Derniers projets"
    link = "/projects/feed"
    description = "Derniers ajouts de projets"

    def items(self):
        return models.Project.objects.order_by("-created_on")[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return reverse("projects-project-detail", args=[item.pk])

    def item_pubdate(self, item):
        return item.created_on


# eof
