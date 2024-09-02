SELECT "projects_project"."id",
    COUNT("tasks_task"."id") AS "task_count"
FROM "projects_project"
    INNER JOIN "projects_projectsite" ON (
        "projects_project"."id" = "projects_projectsite"."project_id"
    )
    LEFT OUTER JOIN "tasks_task" ON (
        "projects_project"."id" = "tasks_task"."project_id"
    )
WHERE (
        "projects_project"."deleted" IS NULL
        AND "projects_projectsite"."site_id" = %s
    )
GROUP BY "projects_project"."id"
