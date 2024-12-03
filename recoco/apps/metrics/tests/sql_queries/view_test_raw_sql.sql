SELECT "projects_project"."id",
    "django_site"."domain" AS "site_domain",
    COUNT("tasks_task"."id") AS "task_count"
FROM "projects_project"
    LEFT OUTER JOIN "projects_projectsite" ON (
        "projects_project"."id" = "projects_projectsite"."project_id"
    )
    LEFT OUTER JOIN "django_site" ON (
        "projects_projectsite"."site_id" = "django_site"."id"
    )
    LEFT OUTER JOIN "tasks_task" ON (
        "projects_project"."id" = "tasks_task"."project_id"
    )
WHERE "projects_project"."deleted" IS NULL 
GROUP BY ("projects_project"."id", "site_domain")
