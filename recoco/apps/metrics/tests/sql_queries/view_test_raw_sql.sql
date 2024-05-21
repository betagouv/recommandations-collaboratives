SELECT "projects_project"."id",
    COUNT("tasks_task"."id") AS "task_count"
FROM "projects_project"
    INNER JOIN "projects_project_sites" ON (
        "projects_project"."id" = "projects_project_sites"."project_id"
    )
    LEFT OUTER JOIN "tasks_task" ON (
        "projects_project"."id" = "tasks_task"."project_id"
    )
WHERE (
        "projects_project"."deleted" IS NULL
        AND "projects_project_sites"."site_id" = %s
    )
GROUP BY "projects_project"."id"
