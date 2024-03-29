# Generated by Django 3.2.13 on 2022-05-04 13:38

from django.db import migrations
import django.db.models.manager
import recoco.apps.resources.models


class Migration(migrations.Migration):
    dependencies = [
        ("resources", "0024_bookmark_site"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="bookmark",
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("on_site", recoco.apps.resources.models.BookmarkOnSiteManager()),
                (
                    "deleted_on_site",
                    recoco.apps.resources.models.DeletedBookmarkOnSiteManager(),
                ),
            ],
        ),
        migrations.AlterModelManagers(
            name="category",
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("on_site", recoco.apps.resources.models.CategoryOnSiteManager()),
                (
                    "deleted_on_site",
                    recoco.apps.resources.models.DeletedCategoryOnSiteManager(),
                ),
            ],
        ),
        migrations.AlterModelManagers(
            name="resource",
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("on_site", recoco.apps.resources.models.ResourceOnSiteManager()),
            ],
        ),
    ]
