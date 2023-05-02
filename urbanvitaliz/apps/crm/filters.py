# -*- mode: python; coding: utf-8; -*-

"""
CRM filters

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: Tue May  2 11:45:15 2023
"""

import django_filters
from django.contrib.auth import models as auth_models

from . import models


class UserFilter(django_filters.FilterSet):
    """Filter for the list of users"""

    ROLE_CHOICES = [
        (0, "Tou·te·s"),
        (1, "Conseiller·ère"),
        (2, "Équipe"),
        (3, "Administrateur·rice"),
    ]

    # filters

    username = django_filters.CharFilter(max_length=255, field_name="username")

    role = django_filters.ChoiceFilter(choices=self.ROLE_CHOICES, method="role_filter")

    active = django_filters.BooleanFilter(field_name="is_active", default=True)

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
    )

    class Meta:
        model = auth_models.User
        fields = ["username", "is_active"]

    def role_filter(self, queryset, name, value):
        return queryset  # .filter()


# eof
