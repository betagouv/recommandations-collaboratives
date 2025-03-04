from watson.search import SearchAdapter

from recoco.utils import strip_accents


class OrganizationSearchAdapter(SearchAdapter):
    fields = (
        "name",
        "departments__name",
        "departments__code",
    )

    def prepare_content(self, content):
        content = super().prepare_content(content)
        return strip_accents(content)


class ContactSearchAdapter(SearchAdapter):
    fields = (
        "last_name",
        "first_name",
        "email",
        "division",
        "organization__name",
        "organization__group__name",
        "organization__departments__name",
        "organization__departments__code",
        "organization__departments__region__name",
        "organization__departments__region__code",
    )

    def prepare_content(self, content):
        content = super().prepare_content(content)
        return strip_accents(content)
