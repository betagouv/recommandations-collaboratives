# -*- mode: python; coding: utf-8; -*-

"""
CRM filters

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: Tue May  2 11:45:15 2023
"""

import django_filters
from django import forms
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from watson import search as watson

from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.geomatics import models as geomatics_models
from recoco.apps.projects import models as projects_models
from recoco.utils import make_group_name_for_site


class OrganizationFilter(django_filters.FilterSet):
    """Filter for the list of organization"""

    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )

    department = django_filters.CharFilter(
        field_name="department",
        lookup_expr="code",
    )

    class Meta:
        model = addressbook_models.Organization
        fields = ["name", "departments"]


class UserFilter(django_filters.FilterSet):
    """Filter for the list of users"""

    ROLE_CHOICES = [
        (1, "Conseiller·ère"),
        (2, "Équipe"),
        (3, "Administrateur·rice"),
        (4, "Autres"),
    ]

    username = django_filters.CharFilter(
        field_name="username",
        lookup_expr="icontains",
    )

    # filters
    role = django_filters.ChoiceFilter(
        label="Rôle",
        empty_label="Tou·te·s",
        choices=ROLE_CHOICES,
        method="role_filter",
        widget=forms.widgets.RadioSelect,
    )

    departments = django_filters.ModelMultipleChoiceFilter(
        label="Départements conseillés",
        field_name="profile__departments",
        queryset=geomatics_models.Department.objects.all(),
    )

    inactive = django_filters.BooleanFilter(
        label="Compte inactif",
        method="inactive_filter",
        widget=forms.widgets.CheckboxInput,
    )

    # orders

    ordering = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ("username", "username"),
            ("last_name", "last_name"),
            ("date_joined", "date_joined"),
        ),
        # labels do not need to retain order
        field_labels={
            "username": "Identifiant de connexion",
            "last_name": "Nom de famille",
            "date_joined": "Date d'inscription",
        },
    )

    class Meta:
        model = auth_models.User
        fields = ["username", "role", "is_active"]

    def inactive_filter(self, queryset, name, value):
        if name != "inactive" or not value:
            return queryset
        return queryset.filter(is_active=False)

    def role_filter(self, queryset, name, value):
        """Filter user having the provided role or all if role is unknown"""
        mapping = {"1": "advisor", "2": "staff", "3": "admin", "4": "others"}

        if name != "role" or value not in mapping.keys():
            return queryset

        name = mapping[value]
        if name == "others":
            return queryset.filter(groups=None)

        site = site_models.Site.objects.get_current()
        group_name = make_group_name_for_site(name, site)
        return queryset.filter(groups__name=group_name)


class ProjectFilter(django_filters.FilterSet):
    """Filter for the list of projects"""

    query = django_filters.CharFilter(
        label="Mots clés",
        method="query_filter",
    )

    commune = django_filters.CharFilter(
        field_name="commune",
        lookup_expr="name__icontains",
    )

    inactive = django_filters.BooleanFilter(
        label="Projet inactifs",
        method="inactive_filter",
        widget=forms.widgets.CheckboxInput,
    )

    ordering = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ("name", "name"),
            ("commune__name", "commune"),
            ("created_on", "created_on"),
        ),
        # labels do not need to retain order
        field_labels={
            "name": "Nom du projet",
            "commune": "Commune",
            "created_on": "Date de dépôt",
        },
    )

    class Meta:
        model = projects_models.Project
        fields = ["name"]

    def query_filter(self, queryset, name, value):
        if name != "query" or not value:
            return queryset
        return watson.filter(queryset, value)

    def inactive_filter(self, queryset, name, value):
        if name != "inactive" or not value:
            return queryset.filter(deleted=None)
        return queryset.exclude(deleted=None)


# eof
