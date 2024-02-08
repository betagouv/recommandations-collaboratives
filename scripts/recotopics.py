# encoding: utf-8

"""
Import topic of tasks from csv file

CSV File:
Taske id,Topic name

One shot file, which does way too many requests.

authors: raphael.marvie@beta.gouv.fr
created: 2023-09-20 07:43:45 CEST
"""

import csv

from recoco.apps.projects import models

DEFAULT_TOPIC = "Tous sujets"


def import_task_topics_from_csv(filename: str) -> None:
    """Import task topics from csv file"""
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)  # skip headers
        update_tasks_with_topics(reader)


def update_tasks_with_topics(rows: list) -> None:
    """Update tasks with given topics from rows or use default topic"""
    for task_id, topic_name in rows:
        topic_name = topic_name.capitalize() or DEFAULT_TOPIC
        task = models.Task.objects.filter(id=task_id).first()
        if not task:
            continue  # happened on prod while not on stagging
        topic, _ = models.Topic.objects.get_or_create(
            name__iexact=topic_name,
            defaults={"name": topic_name, "site": task.site},
        )
        task.topic = topic
        task.save()


# eof
