#!/usr/bin/env python
# coding: utf-8
# %%


# Initialize Notebook

from notebooks.django_for_jupyter import init_django

init_django("recoco")


# %%


from IPython.display import Image

from recoco.apps.projects.models import Project

# # Les composants

# Ceci est un composant :


# %%


get_ipython().run_line_magic("pinfo", "Project")


# %%


image = get_ipython().system(
    "python manage.py graph_models tasks reminders -o models.png"
)


# %%


Image("models.png")


# %%


from IPython.display import HTML
from django.template import Context, Template

# %%


projects = Project.objects.all()


# %%


template = Template(
    """
<table>
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
"""
)

context = Context({"projects": projects.order_by("-created_on")[:10]})

HTML(template.render(context))

# eof
