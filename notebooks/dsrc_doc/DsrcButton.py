#!/usr/bin/env python
# coding: utf-8
# %%
# Initialize Notebook

from notebooks.django_for_jupyter import init_django

init_django("urbanvitaliz")


# %%

from django.db.models import Model
from urbanvitaliz.apps.projects.models import Project



# %%

from django.template import Context, Template
from IPython.display import display, HTML


# %%


projects = Project.objects.all()


# %%


# Load CSS files as raw text using python
"""
Read a CSS or JS file and load it into Jupyter.
Make sure you trust the code you are loading.

Arg: the file path to the file, relative to the project's static assets folder
Returns: IPython.core.display.HTML object: contains JS/CSS in `data` property
"""


def _load_asset(rel_file_path):
    assets_folder = "static/assets/"
    assets_file_path = f"{assets_folder}{rel_file_path}"
    asset_content = open(assets_file_path, "r").read()
    asset = "%s" % asset_content
    return HTML(asset)


csscore = _load_asset("css/dsrc-csscore.css")
csstokens = _load_asset("css/dsrc-csstokens.css")
button_component = _load_asset("index.js")
# print(button_component)
# print(csscore.data)


# %%


template = Template(
    """
{% load static %}
{% load dsrc_tags %}
{% block css %}
    <style>
        {{csscore}}
    </style>
{% endblock %}

{% dsrc_button data_dict %}
"""
)

data_dict = {
    "label": "Label of the button item",
    "onclick": "button action",
    "type": "(Optional) type of button (submit or button - default: submit)",
    "name": "(Optional) name of the button",
    "is_disabled": "(Optional) boolean that indicate if the button is activated (default: False)",
    "extra_classes": "(Optional) string with names of extra classes."
}

context = Context(
    {"data_dict": data_dict, "csscore": csscore.data}
)

HTML(template.render(context))


# %%





# %%
