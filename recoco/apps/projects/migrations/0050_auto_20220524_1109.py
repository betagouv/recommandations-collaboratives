# Generated by Django 3.2.13 on 2022-05-24 09:09

import django.db.models.deletion
from django.conf import settings
from django.contrib.auth.models import User
from django.db import migrations, models


def make_members_from_emails(apps, schema_editor):
    Project = apps.get_model("projects", "Project")  # noqa
    ProjectMember = apps.get_model("projects", "ProjectMember")  # noqa
    db_alias = schema_editor.connection.alias

    for p in Project.objects.using(db_alias).all():
        # First, add owner
        owner, _ = User.objects.using(db_alias).get_or_create(
            username=p.email, defaults={"email": p.email}
        )
        ProjectMember.objects.using(db_alias).create(
            project=p, member_id=owner.id, is_owner=True
        )

        # Then add collaborators
        for email in p.emails:
            user, _ = User.objects.using(db_alias).get_or_create(
                username=email, defaults={"email": email}
            )
            ProjectMember.objects.using(db_alias).get_or_create(
                project=p, member_id=user.id
            )


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("projects", "0049_alter_taskfollowup_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectMember",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_owner", models.BooleanField(default=False)),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "unique_together": {("member", "project")},
            },
        ),
        migrations.AddField(
            model_name="project",
            name="members",
            field=models.ManyToManyField(
                through="projects.ProjectMember", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.RunPython(make_members_from_emails, lambda x, y: None),
    ]
