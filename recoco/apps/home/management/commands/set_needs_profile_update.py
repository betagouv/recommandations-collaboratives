#!/usr/bin/env python

from django.core.management.base import BaseCommand

from recoco.apps.home.models import UserProfile


def set_needs_profile_update():
    user_mandatory_fields = ["first_name", "last_name"]

    profile_mandatory_fields = ["phone_no", "organization", "organization_position"]

    for profile in UserProfile.objects.filter(needs_profile_update=False):
        profile.needs_profile_update = any(
            [
                getattr(profile, field_name) in (None, "")
                for field_name in profile_mandatory_fields
            ]
        ) or any(
            [
                getattr(profile.user, field_name) in (None, "")
                for field_name in user_mandatory_fields
            ]
        )

        profile.save()
    # set(field=And(F(1, isnull), ...)


class Command(BaseCommand):
    help = "Update permissions for User and Groups"

    def handle(self, *args, **options):
        set_needs_profile_update()
