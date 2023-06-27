# encoding: utf-8

"""
Tags common to the complete project

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-06-27 15:52:06 CEST
"""

from django import template

from urbanvitaliz import verbs

register = template.Library()


@register.simple_tag
def get_verbs():
    """Returns verbs used in signals and notification"""
    return verbs


# eof
