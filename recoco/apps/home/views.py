# encoding: utf-8

"""
Views for home application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-08-16 15:40:08 CEST
"""

import urllib

import django.core.mail
from actstream import action
from allauth.account.adapter import get_adapter
from allauth.account.utils import complete_signup, perform_login
from allauth.account.views import (
    EmailVerificationSentView as AllauthEmailVerificationSentView,
)
from allauth.account.views import RequestLoginCodeView
from allauth.mfa.models import Authenticator
from django.contrib import messages
from django.contrib.auth import login as log_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import Count, F, Prefetch, Q
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme, urlencode
from django.views.decorators.csrf import requires_csrf_token
from django.views.defaults import ERROR_403_TEMPLATE_NAME
from django.views.generic import FormView, View
from django.views.generic.base import TemplateView
from notifications.signals import notify

from recoco import verbs
from recoco.apps.geomatics.models import Department
from recoco.apps.projects import models as projects
from recoco.apps.projects.utils import (
    can_administrate_project,
    is_project_moderator_or_403,
)
from recoco.apps.resources import models as resources_models
from recoco.apps.tasks import models as tasks
from recoco.utils import (
    check_if_advisor,
    get_admin_for_site,
    get_staff_for_site,
    is_sensitive_account,
)

from . import models
from .config import EMAIL_CONFIRMATION_FLOW_SESSION_KEY, SIGNUP_USER_ID_SESSION_KEY
from .forms import (
    AdvisorAccessRequestForm,
    ContactForm,
    SiteCreateForm,
    TwoFaConfigForm,
    UserPasswordFirstTimeSetupForm,
)
from .models import AdvisorAccessRequest
from .utils import get_current_site_sender_email, make_new_site


class HomePageView(TemplateView):
    template_name = "home/home.html"


@method_decorator([login_required], name="dispatch")
class LoginRedirectView(View):
    def dispatch(self, request, *args, **kwargs):
        if check_if_advisor(request.user) or can_administrate_project(
            project=None, user=request.user
        ):
            return redirect("projects-project-list")

        projects = request.session.get("projects", None)

        if projects is not None and len(projects) > 0:
            return redirect("projects-project-detail-conversations", projects[0]["id"])

        return redirect("home")


class RegionalActorsPageView(TemplateView):
    template_name = "home/regional_actors.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_switchtender"] = check_if_advisor(self.request.user)
        return context


class MethodologyPageView(TemplateView):
    template_name = "home/methodology.html"


class WhoWeArePageView(TemplateView):
    template_name = "home/whoweare.html"


class LegalsPageView(TemplateView):
    template_name = "home/legals.html"


class TermsOfUsePageView(TemplateView):
    template_name = "home/terms_of_use.html"


class SecurityPageView(TemplateView):
    template_name = "home/security.html"


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
        the_projects = projects.Project.on_site.exclude(
            Q(exclude_stats=True)
            | Q(project_sites__status__in=["DRAFT", "PRE_DRAFT", "REJECTED"])
        )

        context = super().get_context_data(**kwargs)
        context["reco_following_pc"] = 78
        context["collectivity_supported"] = the_projects.count()

        the_tasks = tasks.Task.on_site.exclude(public=False).filter(
            project__in=the_projects
        )
        context["collectivity_with_reco"] = (
            the_tasks.order_by("project_id")
            .values("project_id")
            .distinct("project_id")
            .count()
        )
        total_recommendation = the_tasks.count()
        context["total_recommendation"] = total_recommendation
        context["collectivity_avg_reco"] = (
            total_recommendation / the_projects.count() if the_projects.exists() else ""
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
        if request.user.is_anonymous:
            # quick fix to unlock brevo while captcha may be weak
            raise PermissionDenied(
                "Le formulaire de contact n'est accessible qu'aux personnes authentifiées"
            )
        form = ContactForm(request.POST, user=request.user)
        if form.is_valid():
            status = send_message_to_team(request, form.cleaned_data)
            notify_user_of_sending(request, status)
            return redirect(next_url)
    else:
        form = ContactForm(user=request.user)
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


class EmailVerificationSentView(AllauthEmailVerificationSentView):
    def get_template_names(self):
        match self.request.session.get(EMAIL_CONFIRMATION_FLOW_SESSION_KEY, None):
            case "onboarding":
                return ["onboarding/onboarding-email-confirm.html"]
            case "advisor":
                return ["home/advisor-access-request-confirm-email.html"]
            case _:
                return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_to_validate"] = get_object_or_404(
            User, pk=self.request.session.get(SIGNUP_USER_ID_SESSION_KEY, None)
        )
        return context


def advisor_access_request_view(request: HttpRequest) -> HttpResponse:
    redirect_url = request.GET.get("next")
    site_config = request.site.configuration
    if not url_has_allowed_host_and_scheme(redirect_url, allowed_hosts=None):
        redirect_url = reverse("home")

    if SIGNUP_USER_ID_SESSION_KEY not in request.session:
        return redirect(
            reverse("accounts-signup"),
            +f"?{urlencode({'next': reverse('advisor-access-request')})}",
        )

    user = User.objects.get(pk=request.session[SIGNUP_USER_ID_SESSION_KEY])

    if check_if_advisor(user):
        return redirect(redirect_url)

    advisor_access_request = (
        AdvisorAccessRequest.objects.filter(user=user, site=request.site)
        .prefetch_related(
            Prefetch(
                "departments",
                queryset=Department.objects.order_by("code"),
            )
        )
        .select_related("user")
        .first()
    )

    departments = [
        {"name": d.name, "code": d.code}
        for d in Department.objects.exclude(code="").order_by("code")
    ]

    selected_departments = (
        [
            department.code
            for department in advisor_access_request.departments.order_by("code")
        ]
        if advisor_access_request
        else []
    )

    if request.method == "GET":
        if advisor_access_request and not advisor_access_request.is_pending:
            return redirect(redirect_url)

        form = AdvisorAccessRequestForm()
        form.fields["departments"].initial = selected_departments

    if request.method == "POST":
        form = AdvisorAccessRequestForm(request.POST)
        if form.is_valid():
            new_request = not advisor_access_request
            if new_request:
                advisor_access_request = AdvisorAccessRequest(
                    site=request.site, user=user
                )

            advisor_access_request.comment = form.cleaned_data.get("comment", "")
            advisor_access_request.save()

            advisor_access_request.departments.set(form.cleaned_data["departments"])

            if new_request:
                notify.send(
                    sender=advisor_access_request.user,
                    recipient=list(
                        set(get_admin_for_site(request.site)).union(
                            get_staff_for_site(request.site)
                        )
                    ),
                    verb=verbs.User.ADVISOR_REQUEST,
                    action_object=advisor_access_request,
                )
                action.send(
                    sender=advisor_access_request.user,
                    verb=verbs.User.ADVISOR_REQUEST,
                    action_object=advisor_access_request,
                )

            request.session[EMAIL_CONFIRMATION_FLOW_SESSION_KEY] = "advisor"
            if new_request:
                return complete_signup(
                    request,
                    user=user,
                    email_verification=None,
                    success_url=reverse("advisor-access-request-pending"),
                )
            return perform_login(
                request,
                user,
                redirect_url=reverse("advisor-access-request-pending"),
            )

    return render(
        request,
        "home/advisor_access_request.html",
        context={
            "site_config": site_config,
            "form": form,
            "advisor_access_request": advisor_access_request,
            "departments": departments,
            "selected_departments": selected_departments,
        },
    )


class AdvisorAccessRequestPendingView(LoginRequiredMixin, TemplateView):
    template_name = "home/advisor-access-request-pending.html"

    def get(self, request, *args, **kwargs):
        if SIGNUP_USER_ID_SESSION_KEY in self.request.session:
            del self.request.session[SIGNUP_USER_ID_SESSION_KEY]
        if EMAIL_CONFIRMATION_FLOW_SESSION_KEY in self.request.session:
            del self.request.session[EMAIL_CONFIRMATION_FLOW_SESSION_KEY]
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["advisor_access_request"] = get_object_or_404(
            AdvisorAccessRequest.objects.filter(
                user=self.request.user, site=self.request.site, status="PENDING"
            )
            .prefetch_related(
                Prefetch(
                    "departments",
                    queryset=Department.objects.order_by("code"),
                )
            )
            .select_related("user")
        )
        return context


@login_required
def advisor_access_request_moderator_view(
    request: HttpRequest, advisor_access_request_id: int
) -> HttpResponse:
    is_project_moderator_or_403(request.user, request.site)

    advisor_access_request = get_object_or_404(
        AdvisorAccessRequest.on_site.prefetch_related("departments").select_related(
            "user"
        ),
        pk=advisor_access_request_id,
    )

    departments = [
        {"name": d.name, "code": d.code}
        for d in Department.objects.exclude(code="").order_by("code")
    ]

    selected_departments = [
        department.code for department in advisor_access_request.departments.all()
    ]

    redirect_url = reverse("projects-moderation-list")

    if request.method == "GET":
        if not advisor_access_request.is_pending:
            return redirect(redirect_url)

        form = AdvisorAccessRequestForm()
        form.fields["departments"].initial = selected_departments
        form.fields["comment"].initial = advisor_access_request.comment
        if advisor_access_request.departments.count() > 0:
            form.fields["advisor_access_type"].initial = "Regional"
        else:
            form.fields["advisor_access_type"].initial = "National"

    if request.method == "POST":
        form = AdvisorAccessRequestForm(request.POST)
        if form.is_valid():
            advisor_access_request.departments.set(form.cleaned_data["departments"])
            messages.add_message(
                request,
                messages.SUCCESS,
                f"{advisor_access_request.user.first_name} {advisor_access_request.user.last_name} a été modifié.",
            )
            return redirect(redirect_url)

    return render(
        request,
        "home/advisor_access_request_moderator.html",
        context={
            "form": form,
            "advisor_access_request": advisor_access_request,
            "departments": departments,
            "selected_departments": selected_departments,
        },
    )


### Site Creation
### 3 tests are at least required: permission enforcement, site creation and
### site creation error (domain already used for eg)
class SiteCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = SiteCreateForm
    permission_required = "sites.add_site"
    template_name = "home/site_create.html"

    def form_valid(self, form):
        try:
            make_new_site(
                name=form.cleaned_data["name"],
                domain=f"{form.cleaned_data['subdomain']}.recoconseil.fr",
                sender_email=form.cleaned_data["sender_email"],
                sender_name=form.cleaned_data["sender_name"],
                contact_form_recipient=form.cleaned_data["contact_form_recipient"],
                legal_address=form.cleaned_data["legal_address"],
                admin_user=self.request.user,
            )
            messages.success(self.request, "Le portail a bien été créé !")
        except Exception as e:
            messages.error(self.request, f"Impossible de créer le portail : {e}")

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("site-create")


@requires_csrf_token
def permission_denied(request, exception):
    # customizes PermissionDenied to customize with next url and user's data

    template = loader.get_template(ERROR_403_TEMPLATE_NAME)
    login_url = (
        reverse("account_login") + "?" + urllib.parse.urlencode({"next": request.path})
    )
    logout_url = (
        reverse("account_logout") + "?" + urllib.parse.urlencode({"next": login_url})
    )

    return HttpResponseForbidden(
        template.render(
            request=request,
            context={
                "exception": str(exception),
                "relogin_url": logout_url,
            },
        )
    )


class RequestLoginCodeNoStaffView(RequestLoginCodeView):
    def form_valid(self, form):
        if form._user and is_sensitive_account(
            form._user, get_current_site(self.request)
        ):
            get_adapter().send_mail(
                "home/email/no_login_by_code_staff",
                form._user.email,
                {"request": self.request},
            )
            return HttpResponseRedirect(self.get_success_url())
        return super().form_valid(form)


@method_decorator([login_required], name="dispatch")
class TwoFAConfigView(FormView):
    form_class = TwoFaConfigForm
    template_name = "home/mfa-config.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_invalid(self, form):
        # at least ensure that requires_2fa is respected
        authenticator = Authenticator.objects.filter(
            type=Authenticator.Type.TOTP, user=self.request.user
        ).first()
        if (
            self.request.user.profile.requires_2fa
            and not authenticator
            and not self.request.user.profile.login_with_code
        ):
            self.request.user.profile.login_with_code = True
            self.request.user.profile.save()
        return super().form_invalid(form)

    def form_valid(self, form):
        two_fa_mode = form.cleaned_data["two_fa_mode"]
        if two_fa_mode == "none":
            self.request.user.profile.login_with_code = False
            self.request.user.profile.save()
            authenticator = Authenticator.objects.filter(
                type=Authenticator.Type.TOTP, user=self.request.user
            ).first()
            if authenticator:
                url = reverse("mfa_deactivate_totp")
                return redirect(url)
        elif two_fa_mode == "totp":
            authenticator = Authenticator.objects.filter(
                type=Authenticator.Type.TOTP, user=self.request.user
            ).first()
            if not authenticator:
                # removing email 2fa is done through a signal
                url = reverse("mfa_activate_totp")
                return redirect(url)
            self.request.user.profile.login_with_code = False
            self.request.user.profile.save()
        else:  # 2fa is set to login with code. totp may or may not have been activated before
            self.request.user.profile.login_with_code = True
            self.request.user.profile.save()

            authenticator = Authenticator.objects.filter(
                type=Authenticator.Type.TOTP, user=self.request.user
            ).first()
            if authenticator:
                url = reverse("mfa_deactivate_totp")
                return redirect(url)

        messages.success(self.request, "Vos paramètres ont bien été sauvegardés.")
        return self.render_to_response(self.get_context_data(form=form))


# eof
