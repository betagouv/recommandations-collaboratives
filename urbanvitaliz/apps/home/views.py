# encoding: utf-8

"""
Views for home application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-08-16 15:40:08 CEST
"""


import django.core.mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as log_user
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.generic.base import TemplateView
from urbanvitaliz.apps.projects import models as projects
from urbanvitaliz.apps.projects.utils import (
    can_administrate_project,
    get_active_project,
)
from urbanvitaliz.utils import check_if_advisor

from .forms import ContactForm, UserPasswordFirstTimeSetupForm


class HomePageView(TemplateView):
    template_name = "home/home.html"


@method_decorator([login_required], name="dispatch")
class LoginRedirectView(View):
    def dispatch(self, request, *args, **kwargs):
        if check_if_advisor(request.user) or can_administrate_project(
            project=None, user=request.user
        ):
            return redirect("projects-project-list")

        project = get_active_project(request)
        if project:
            return redirect("projects-project-detail-actions", project.pk)

        return redirect("home")


class RegionalActorsPageView(TemplateView):
    template_name = "home/regional_actors.html"


class MethodologyPageView(TemplateView):
    template_name = "home/methodology.html"


class WhoWeArePageView(TemplateView):
    template_name = "home/whoweare.html"


class LegalsPageView(TemplateView):
    template_name = "home/legals.html"


class TermsOfUsePageView(TemplateView):
    template_name = "home/terms_of_use.html"


class PrivacyPageView(TemplateView):
    template_name = "home/privacy.html"


class FollowUsPageView(TemplateView):
    template_name = "home/followus.html"


class StatisticsView(TemplateView):
    template_name = "home/statistics.html"

    def get_context_data(self, **kwargs):
        staff_users = auth.User.objects.filter(is_staff=True)
        the_projects = projects.Project.on_site.exclude(
            Q(members__in=staff_users)
            | Q(status="DRAFT")
            | Q(status="STUCK")
            # FIXME ^ replace w/: | Q(status="STANDBY")
            | Q(exclude_stats=True)
        )
        context = super().get_context_data(**kwargs)
        context["reco_following_pc"] = 90
        context["collectivity_supported"] = the_projects.count()
        context["collectivity_with_reco"] = (
            projects.Task.on_site.exclude(
                Q(status=projects.Task.NOT_INTERESTED)
                | Q(status=projects.Task.ALREADY_DONE)
            )
            .exclude(
                Q(project__members__in=staff_users)
                | Q(project__status="DRAFT")
                | Q(project__status="STUCK")
                # FIXME ^ replace w/: | Q(project__status="STANDBY")
                | Q(project__exclude_stats=True)
            )
            .order_by("project_id")
            .values("project_id")
            .distinct("project_id")
            .count()
        )
        numbers = [
            p.number_tasks
            for p in the_projects.all().annotate(number_tasks=Count("tasks"))
        ]
        context["collectivity_avg_reco"] = sum(numbers) / len(numbers) if numbers else 0

        context["new_col_per_month"] = [
            (f"{p['month']}/{p['year']}", p["total"])
            for p in the_projects.order_by("created_on__year", "created_on__month")
            .values(year=F("created_on__year"), month=F("created_on__month"))
            .annotate(total=Count("id"))
        ][-10:]

        context["collectivity_geo"] = (
            (p["latitude"], p["longitude"])
            for p in the_projects.exclude(commune=None).values(
                latitude=F("commune__latitude"), longitude=F("commune__longitude")
            )
        )

        return context


def contact(request):
    """Sends an email to the team with contact info from user"""
    next_url = request.GET.get("next", "/")
    if request.method == "POST":
        form = ContactForm(request.user, request.POST)
        if form.is_valid():
            status = send_message_to_team(request, form.cleaned_data)
            notify_user_of_sending(request, status)
            return redirect(next_url)
    else:
        form = ContactForm(request.user)
    return render(request, "home/contact.html", locals())


def send_message_to_team(request, data):
    """Send message as email to the team"""
    subject = data.get("subject")
    content = data.get("content")
    if request.user.is_authenticated:
        content += f"\n\nfrom: {request.user.email}"
    else:
        name = data.get("name")
        email = data.get("email")
        content += f"\n\nfrom: {name} {email}"
    content += "\nsource: " + request.META.get("HTTP_REFERER", "")
    return django.core.mail.send_mail(
        subject=subject,
        message=content,
        from_email=settings.EMAIL_FROM,
        recipient_list=settings.TEAM_EMAILS,
        fail_silently=True,
    )


def notify_user_of_sending(request, status):
    """Notify user of sending request through message framework"""
    if status:
        messages.success(
            request, "Merci, votre demande a été transmis à l'équipe Urbanvitaliz !"
        )
    else:
        messages.error(
            request,
            "Désolé, nous n'avons pas réussi à envoyer votre courriel. "
            "Vous pouvez réessayer "
            "ou utiliser l'adresse depuis votre logiciel de messagerie",
        )


@login_required
def setup_password(request):
    """A simple view that request a password for a user that doesn't have one yet"""
    next_url = request.GET.get("next", "/")

    # We have a password, redirect!
    if request.user.password:
        return redirect(next_url)

    if request.method == "POST":
        form = UserPasswordFirstTimeSetupForm(request.POST)
        next_url = request.POST.get("next", "/")
        if form.is_valid():
            request.user.set_password(form.cleaned_data.get("password1"))
            request.user.save()
            log_user(
                request,
                request.user,
                backend="django.contrib.auth.backends.ModelBackend",
            )

            return redirect(next_url)
    else:
        form = UserPasswordFirstTimeSetupForm(initial={"next": next_url})

    return render(request, "home/user_setup_password.html", locals())


# eof
