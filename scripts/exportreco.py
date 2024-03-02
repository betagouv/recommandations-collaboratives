"""
Script to extract all tasks
"""

import csv

from recoco.apps.projects.models import Task

headers = [
    "# reco",
    "# ressource",
    "Titre resource",
    "# projet",
    "Desc projet",
    "Commune insee",
    "Commune nom",
    "Thematiques projets",
    "Contenu reco",
]

all_tasks = (
    Task.on_site.all()
    .prefetch_related("project__commune", "resource")
    .prefetch_related("project__topics")
)

data = []

for task in all_tasks:
    data.append(
        [
            task.id,
            task.resource.id if task.resource else "",
            task.resource.title if task.resource else "",
            task.project.id,
            task.project.description,
            task.project.commune.insee,
            task.project.commune.name,
            ",".join([t.name for t in task.project.topics.all()]),
            task.content,
        ]
    )

with open("reco.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(data)

# eof
