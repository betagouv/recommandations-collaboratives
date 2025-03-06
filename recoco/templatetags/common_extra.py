# encoding: utf-8

"""
Tags common to the complete project

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-06-27 15:52:06 CEST
"""

import os

from django import template

from recoco import verbs
from recoco.utils import check_if_advisor

register = template.Library()


@register.simple_tag
def get_verbs():
    """Returns verbs used in signals and notification"""
    return verbs


@register.filter
def filename(value):
    return os.path.basename(value.file.name)


@register.simple_tag
def is_advisor_for_site(user, site=None):
    return check_if_advisor(user, site)


# eof
