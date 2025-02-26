#!/usr/bin/env python
# coding: utf-8
# %%

# # Assigner des utilisateurs à des dossiers

# %%


import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"  # Pas besoin en dehors de Jupyter


# %%


# coding: utf-8
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from recoco.apps.projects.models import Project

user = User.objects.first()
print(user)

project = Project.objects.get(pk=20)
print(project)

site = Site.objects.get_current()
print(site)


# %%


from recoco.apps.projects.utils import (
    assign_advisor,
    assign_collaborator,
    assign_observer,
)

print(assign_advisor.__doc__)


# %%


get_ipython().run_line_magic("pinfo", "assign_collaborator")

# Assigner un utilisateur sur un dossier
assign_collaborator(user, project, is_owner=False)


# %%


# Assigner des conseillers et observateurs
get_ipython().run_line_magic("pinfo", "assign_advisor")

assign_advisor(user, project, site)

# et observateurs
assign_observer(user, project, site)


# %%


# eof
