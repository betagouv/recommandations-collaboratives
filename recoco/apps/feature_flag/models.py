"""
https://waffle.readthedocs.io/en/stable/types/flag.html
"""

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.sites.models import Site
from django.db import models
from django.http import HttpRequest
from waffle.models import AbstractBaseSample, AbstractBaseSwitch, AbstractUserFlag


class SitesMixin(models.Model):
    class Meta:
        abstract = True

    sites = models.ManyToManyField(
        Site,
        blank=True,
        help_text="Activate for these sites.",
    )

    def is_active_for_current_site(self, request: HttpRequest | None = None) -> bool:
        if self.pk and self.sites.exists():
            return Site.objects.get_current(request) in self.sites.all()
        return True

    def get_queryset(self):
        return super().get_queryset().prefetch_related("sites")


class Switch(SitesMixin, AbstractBaseSwitch):
    def is_active(self) -> bool | None:
        if not self.is_active_for_current_site():
            return False
        return super().is_active()


class Flag(SitesMixin, AbstractUserFlag):
    def is_active_for_user(self, user: AbstractBaseUser) -> bool | None:
        if not self.is_active_for_current_site():
            return False
        return super().is_active_for_user(user)

    def is_active(self, request: HttpRequest, read_only: bool = False) -> bool | None:
        if not self.is_active_for_current_site(request):
            return False
        return super().is_active(request, read_only)


class Sample(SitesMixin, AbstractBaseSample):
    def is_active(self) -> bool | None:
        if not self.is_active_for_current_site():
            return False
        return super().is_active()
