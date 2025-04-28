# encoding: utf-8

"""
Views for home application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-08-16 15:40:08 CEST
"""

import django.core.mail
from django.contrib import messages
from django.contrib.auth import login as log_user
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Count, F, Q
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import View
from django.views.generic.base import TemplateView

from recoco.apps.onboarding.forms import OnboardingEmailForm
from recoco.apps.projects import models as projects
from recoco.apps.projects.utils import can_administrate_project
from recoco.apps.resources import models as resources_models
from recoco.apps.tasks import models as tasks
from recoco.utils import check_if_advisor, require_htmx

from . import models
from .forms import AdvisorAccessRequestForm, ContactForm, UserPasswordFirstTimeSetupForm
from .models import AdvisorAccessRequest
from .utils import get_current_site_sender_email


class HomePageView(TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["onboarding_modal_form"] = OnboardingEmailForm()
        return context


@method_decorator([login_required], name="dispatch")
class LoginRedirectView(View):
    def dispatch(self, request, *args, **kwargs):
        if check_if_advisor(request.user) or can_administrate_project(
            project=None, user=request.user
        ):
            return redirect("projects-project-list")

        projects = request.session.get("projects", None)

        if projects:
            return redirect("projects-project-detail-actions", projects[0]["id"])

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


class AccessibiltyPageView(TemplateView):
    template_name = "home/accessibility.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sender_email"] = get_current_site_sender_email()
        return context


class MutliAnnualSchemaPageView(TemplateView):
    template_name = "home/multi_annual_schema.html"


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
            # FIXME ^ replace w/: | Q(status="STANDBY") -> OK
            | Q(exclude_stats=True)
        ).exclude(
            project_sites__site=self.request.site,
            project_sites__status__in=["DRAFT", "STUCK"],
        )

        context = super().get_context_data(**kwargs)
        context["reco_following_pc"] = 78
        context["collectivity_supported"] = the_projects.count()
        context["collectivity_with_reco"] = (
            tasks.Task.on_site.exclude(
                Q(status=tasks.Task.NOT_INTERESTED) | Q(status=tasks.Task.ALREADY_DONE)
            )
            .exclude(
                Q(project__members__in=staff_users)
                # FIXME ^ replace w/: | Q(project__status="STANDBY")
                | Q(project__exclude_stats=True)
            )
            .exclude(
                project__project_sites__status__in=["DRAFT", "STUCK"],
                project__project_sites__site=self.request.site,
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
        context["total_recommendation"] = sum(numbers)
        context["collectivity_avg_reco"] = (
            context["total_recommendation"] / len(numbers) if numbers else 0
        )

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

        context["resource_count"] = resources_models.Resource.on_site.exclude(
            status=resources_models.Resource.DRAFT
        ).count()

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
    content += "\nsource: " + request.headers.get("referer", "")

    try:
        site_config = request.site.configuration
    except models.SiteConfiguration.DoesNotExist as exc:
        raise ImproperlyConfigured(
            f"Please create the SiteConfiguration for this site '{request.site}'"
        ) from exc

    recipient = site_config.contact_form_recipient

    # Try to get the current user email if logged in, otherwise default to current site
    # sender
    sender_email = site_config.sender_email
    if not request.user.is_anonymous and request.user.email:
        sender_email = request.user.email

    return django.core.mail.send_mail(
        subject=subject,
        message=content,
        from_email=sender_email,
        recipient_list=[recipient],
        fail_silently=True,
    )


def notify_user_of_sending(request, status):
    """Notify user of sending request through message framework"""
    if status:
        messages.success(
            request,
            "Merci, votre demande a été transmis à l'équipe {{ request.site.name }} !",
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


@login_required
def advisor_access_request_view(request: HttpRequest):
    redirect_url = request.GET.get("next", "/")

    if check_if_advisor(request.user):
        return redirect(redirect_url)

    form = AdvisorAccessRequestForm(request.POST or None)

    advisor_access_request: AdvisorAccessRequest = None

    if request.method == "GET":
        advisor_access_request = AdvisorAccessRequest.objects.filter(
            user=request.user, site=request.site
        ).first()

        if advisor_access_request:
            if not advisor_access_request.is_pending:
                return redirect(redirect_url)

            form.fields["departments"].initial = [
                department.id for department in advisor_access_request.departments.all()
            ]

    if request.method == "POST":
        advisor_access_request = form.save(commit=False)
        advisor_access_request.site = request.site
        advisor_access_request.user = request.user
        advisor_access_request.save()

    return render(
        request,
        "home/advisor_access_request.html",
        context={
            "form": form,
            "advisor_access_request": advisor_access_request,
        },
    )


@login_required
@require_http_methods(["POST"])
@require_htmx
def advisor_access_request_accept_view(
    request: HttpRequest, advisor_access_request_id: int
):
    advisor_access_request = get_object_or_404(
        AdvisorAccessRequest, pk=advisor_access_request_id
    )
    advisor_access_request.accept(handled_by=request.user)


@login_required
@require_http_methods(["POST"])
@require_htmx
def advisor_access_request_reject_view(
    request: HttpRequest, advisor_access_request_id: int
):
    advisor_access_request = get_object_or_404(
        AdvisorAccessRequest, pk=advisor_access_request_id
    )
    advisor_access_request.reject(handled_by=request.user)


# eof
