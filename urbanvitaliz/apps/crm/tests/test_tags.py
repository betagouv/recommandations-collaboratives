import collections

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone
from guardian.shortcuts import assign_perm
from model_bakery import baker
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import get_group_for_site, login

from .. import models, views


########################################################################
# tag cloud
########################################################################


@pytest.mark.django_db
def test_compute_tag_cloud():
    site = baker.make(site_models.Site)
    project_annotation = baker.make(models.ProjectAnnotations, site=site)
    project_annotation.tags.add("tag0", "tag1")
    note = baker.make(models.Note, site=site, related=project_annotation.project)
    note.tags.add("tag0", "tag2")
    tags = views.compute_tag_occurences(site)
    assert tags == collections.OrderedDict(
        {
            "tag0": 2,
            "tag1": 1,
            "tag2": 1,
        }
    )


# eof
