import collections

import pytest
from django.contrib.sites import models as site_models
from model_bakery import baker

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
