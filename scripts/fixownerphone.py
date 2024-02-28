from django.conf import settings
from django.contrib.sites.models import Site
from recoco.apps.projects import models as projects_models


# pour chaque site
for site in Site.objects.all():
    with settings.SITE_ID.override(site.pk):
        # collect owners without phone numbers
        # and project containing phone number

        owners = (
            projects_models.ProjectMember.objects.filter(is_owner=True)
            .filter(member__profile__phone_no="")
            .exclude(project__phone="")
            .prefetch_related("project")
        )

        # fix missing owner phone numbers by using project if last_name matches

        for pm in owners:
            # if name of owner and project are diffrent skip
            if pm.member.last_name.lower() != pm.project.last_name.lower():
                continue
            # update missing phone number
            profile = pm.member.profile
            profile.phone_no = pm.project.phone
            profile.save()

            print(
                "Updated:",
                profile.user.last_name,
                profile.organization,
                profile.phone_no,
            )

# eof
