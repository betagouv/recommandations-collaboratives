WITH taskfollowup AS (
    SELECT
        projects_taskfollowup.id,
        projects_taskfollowup.task_id,
        auth_user.email
    FROM
        projects_taskfollowup
    INNER JOIN auth_user
        ON projects_taskfollowup.who_id = auth_user.id
)
SELECT
    projects_project.id,
    projects_project.name,
    projects_task.done AS task_done,
    projects_task.id AS task_id,
    reminders_mail.id AS reminder_id,
    taskfollowup.id AS followup_id
FROM
    projects_task
INNER JOIN projects_project
    ON projects_task.project_id = projects_project.id
LEFT JOIN reminders_mail
    ON (reminders_mail.object_id = projects_task.id
        AND reminders_mail.content_type_id = 10  
        AND reminders_mail.origin = 1)  
LEFT JOIN taskfollowup
    ON (taskfollowup.task_id = projects_task.id
        AND (projects_project.emails ? taskfollowup.email))
WHERE
    projects_task.done IS TRUE
    OR reminders_mail.id IS NOT NULL
    OR taskfollowup.id IS NOT NULL


;
