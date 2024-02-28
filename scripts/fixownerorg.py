from django.conf import settings
from django.contrib.sites.models import Site
from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.projects import models as projects_models

# pour chaque site
for site in Site.objects.all():
    with settings.SITE_ID.override(site.pk):
        # collect project owners with missing organization
        # and project having an org name

        owners = (
            projects_models.ProjectMember.objects.filter(is_owner=True)
            .filter(member__profile__organization=None)
            .exclude(project__org_name="")
            .prefetch_related("project")
        )

        # fix missing owner organization by using project if last_name matches

        for pm in owners:
            # if name of owner and project are diffrent skip
            if pm.member.last_name.lower() != pm.project.last_name.lower():
                continue
            # update missing phone number
            profile = pm.member.profile
            org = addressbook_models.Organization.get_or_create(pm.project.org_name)
            org.sites.add(site)
            profile.organization = org
            profile.save()

            print("Updated:", profile.user.last_name, profile.organization)

# eof
