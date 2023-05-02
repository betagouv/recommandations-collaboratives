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
from urbanvitaliz.utils import make_group_name_for_site

from . import models


class UserFilter(django_filters.FilterSet):
    """Filter for the list of users"""

    ROLE_CHOICES = [
        (1, "Conseiller·ère"),
        (2, "Équipe"),
        (3, "Administrateur·rice"),
    ]

    # filters
    role = django_filters.ChoiceFilter(
        label="Rôle",
        empty_label="Tou·te·s",
        choices=ROLE_CHOICES,
        method="role_filter",
        widget=forms.widgets.RadioSelect,
    )

    is_active = django_filters.BooleanFilter(
        label="Compte actif", field_name="is_active", widget=forms.widgets.CheckboxInput
    )

    # orders

    ordering = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ("last_name", "last_name"),
            ("created_on", "created_on"),
        ),
        # labels do not need to retain order
        field_labels={
            "last_name": "Nom de famille",
            "created_on": "Date de création",
        },
        widget=django_filters.widgets.LinkWidget,
    )

    class Meta:
        model = auth_models.User
        fields = []

    def role_filter(self, queryset, name, value):
        """Filter user having the provided role or all if role is unknown"""
        if name != "role":
            return queryset

        # get requested group name
        mapping = {1: "advisor", 2: "staff", 3: "admin"}
        name = mapping.get(value)
        if not name:
            return queryset

        # filter on group name
        site = site_models.Site.objects.get_current()
        group_name = make_group_name_for_site(name, site)
        return queryset.filter(group__name=group_name)


# eof
