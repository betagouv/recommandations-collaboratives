# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from django.contrib.syndication.views import Feed
from django.urls import reverse

from .. import models

########################################################################
# RSS Feeds
########################################################################


class LatestProjectsFeed(Feed):
    title = "Derniers projets"
    link = "/projects/feed"
    description = "Derniers ajouts de projets"

    def items(self):
        return models.Project.on_site.order_by("-created_on")[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return reverse("projects-project-detail", args=[item.pk])

    def item_pubdate(self, item):
        return item.created_on


# eof
