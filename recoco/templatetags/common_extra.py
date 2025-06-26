# encoding: utf-8

"""
Tags common to the complete project

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-06-27 15:52:06 CEST
"""

import os

from django import template

from recoco import verbs

register = template.Library()


@register.simple_tag
def get_verbs():
    """Returns verbs used in signals and notification"""
    return verbs


@register.filter
def filename(value):
    return os.path.basename(value.file.name)


@register.filter
def template_exists(template_name: str) -> bool:
    try:
        template.loader.get_template(template_name)
        return True
    except template.TemplateDoesNotExist:
        return False


# eof
