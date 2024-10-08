"""
Migrate ProjectTopic to Topic into project.topics
"""

from django.conf import settings
from django.contrib.sites.models import Site

from recoco.apps.projects import models as projects_models

# pour chaque site
for site in Site.objects.all():
    with settings.SITE_ID.override(site.pk):
        # all project topic -> topic to project
        for tp in projects_models.ProjectTopic.objects.all():
            topic, _ = projects_models.Topic.objects.get_or_create(
                site=tp.site,
                name__iexact=tp.label.lower(),
                defaults={"name": tp.label.capitalize(), "site": tp.site},
            )
            tp.project.topics.add(topic)

# eof
