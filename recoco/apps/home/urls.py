# encoding: utf-8

"""
Urls for projects application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-05-26 15:54:25 CEST
"""

from django.conf import settings
from django.urls import path

from . import views
from .views import RequestLoginCodeNoStaffView

urlpatterns = [
    path(
        r"",
        views.HomePageView.as_view(),
        name="home",
    ),
    path(
        r"login-redirect",
        views.LoginRedirectView.as_view(),
        name="login-redirect",
    ),
    path(
        r"stats",
        views.StatisticsView.as_view(),
        name="statistics",
    ),
    path(
        r"methodologie",
        views.MethodologyPageView.as_view(),
        name="methodology",
    ),
    path(
        r"acteurs-locaux",
        views.RegionalActorsPageView.as_view(),
        name="regional-actors",
    ),
    path(
        r"qui-sommes-nous",
        views.WhoWeArePageView.as_view(),
        name="whoweare",
    ),
    path(
        r"confidentialite",
        views.PrivacyPageView.as_view(),
        name="privacy",
    ),
    path(
        r"conditions-generales-utilisation",
        views.TermsOfUsePageView.as_view(),
        name="termsofuse",
    ),
    path(
        r"mentions-legales",
        views.LegalsPageView.as_view(),
        name="legals",
    ),
    path(
        r"securite",
        views.SecurityPageView.as_view(),
        name="security",
    ),
    path(
        r"accessibilite",
        views.AccessibiltyPageView.as_view(),
        name="accessibility",
    ),
    path(
        r"schema-multi-annuel",
        views.MutliAnnualSchemaPageView.as_view(),
        name="multi-annual-schema",
    ),
    path(
        r"nous-suivre",
        views.FollowUsPageView.as_view(),
        name="followus",
    ),
    path(
        r"contact/",
        views.contact,
        name="home-contact",
    ),
    path(
        r"setup-password/",
        views.setup_password,
        name="home-user-setup-password",
    ),
    path(  # form part 2 : profile (part 1 is signup)
        r"advisor-access-request",
        views.advisor_access_request_view,
        name="advisor-access-request",
    ),
    # step 3 for email confirmation is included in login stage
    path(  # success page : request is pending
        r"advisor-access-request/pending",
        views.AdvisorAccessRequestPendingView.as_view(),
        name="advisor-access-request-pending",
    ),
    path(  # moderation part
        r"advisor-access-request/<int:advisor_access_request_id>/",
        views.advisor_access_request_moderator_view,
        name="advisor-access-request-moderator",
    ),
    path(r"site/create", views.SiteCreateView.as_view(), name="site-create"),
    # I use same view name to facilitate redirects
    path(r"2fa-config", views.TwoFAConfigView.as_view(), name="mfa_index"),
    path(
        "confirm-email/",
        views.EmailVerificationSentView.as_view(),
        name="account_email_verification_sent",
    ),
]

if settings.ACCOUNT_LOGIN_BY_CODE_ENABLED:
    urlpatterns.extend(
        [
            path(
                "login/code/",
                RequestLoginCodeNoStaffView.as_view(),
                name="account_request_login_code",
            ),
        ]
    )

# eof
