
from django.conf import settings
from django.contrib.sites.models import Site
from urbanvitaliz.apps.projects import models as projects_models


# pour chaque site
for site in Site.objects.all():

    with settings.SITE_ID.override(site.pk):

        # collect peojects w/o submitted_by

        projects = projects_models.Project.objects.filter(submitted_by=None)

        # fix missing submitted by using owner when matching project last_name
        # (or last_name missing)

        for p in projects:
            # for the moment skip project w/o owner
            if not p.owner:
                continue
            # if there is a project last_name and it differs from owner skip
            if p.last_name and p.last_name.lower() != p.owner.last_name.lower():
                continue
            # we consider current owner to be sumitter
            p.submitted_by = p.owner
            p.save()

# eof
