--
-- reporting on comment usage
COPY (
    SELECT
        f.timestamp AS quand,
        u.username AS qui,
        t.id AS reco
    FROM
        projects_taskfollowup f
    LEFT JOIN auth_user u ON f.who_id = u.id
    LEFT JOIN projects_task t ON f.task_id = t.id
    LEFT JOIN projects_project p ON t.project_id = p.id
WHERE
    p.exclude_stats = 'f'
ORDER BY
    f.timestamp)
TO '/tmp/comment.csv' DELIMITER ',' csv header;

-- eof
