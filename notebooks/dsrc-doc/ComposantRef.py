#!/usr/bin/env python
# coding: utf-8
# %%

from django.db.models import Model
import os
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


# %%


from urbanvitaliz.apps.projects.models import Project


# # Les composants

# Ceci est un composant :

# %%


get_ipython().run_line_magic('pinfo', 'Project')


# %%


from graphviz import Source
from IPython.display import Image


# %%


get_ipython().system('python manage.py graph_models tasks reminders -o models.png 2>/dev/null')
Image('models.png')


# %%


from django.template import Context, Template
from IPython.display import HTML



# %%


projects = Project.objects.all()


# %%


template = Template("""
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
""")

context = Context(
    {'projects': projects.order_by("-created_on")[:10]}
)

HTML(template.render(context))


# %%





# %%




