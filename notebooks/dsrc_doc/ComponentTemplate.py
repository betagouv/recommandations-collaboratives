#!/usr/bin/env python
# coding: utf-8
# %%
# Initialize Notebook

from notebooks.django_for_jupyter import init_django

init_django("urbanvitaliz")


# %%


from urbanvitaliz.apps.projects.models import Project
from django.db.models import Model


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


csscore = _load_asset("dsrc-csscore.css")
csstokens = _load_asset("dsrc-csstokens.css")
button_component = _load_asset("components/DsrcButton.js")
# print(button_component)
# print(csscore.data)


# %%


template = Template(
    """

{% load static %}
{% load sass_tags %}
{% load django_vite %}
{% block css %}
    <style>
        {{csscore}}
    </style>
{% endblock %}

<table class="fr-table">
    <tr>
        <th>Projet</th>
        <th>Ville</th>
        <th>Gigs</th>
    </tr>
    {% for p in projects %}
    <tr>
        <td>{{p.name}}</td>
        <td>{{p.created_on}}</td>
        <td>{{p.location}}</td>
    </tr>
    {% endfor %}
</table>
<ul class="fr-btns-group fr-btns-group--inline-sm unstyled">
    <li>
        <button class="fr-btn">Bouton</button>
    </li>
    <li>
        <button class="fr-btn fr-btn--secondary">Bouton Secondaire</button>
    </li>
    <li>
        <button class="fr-btn fr-btn--tertiary">Bouton Tertiaire</button>
    </li>
</ul>
"""
)

context = Context(
    {"projects": projects.order_by("-created_on")[:5], "csscore": csscore.data}
)

HTML(template.render(context))


# %%

# eof

# %%
