--
-- reporting on switchtenders activity
COPY (
    SELECT
        p.id AS id,
        p.name AS project,
        u.username AS aigu
    FROM
        projects_project_switchtenders s
    LEFT JOIN projects_project p ON s.project_id = p.id
    LEFT JOIN auth_user u ON s.user_id = u.id
WHERE
    p.exclude_stats = 'f'
ORDER BY
    u.username)
TO '/tmp/aigui.csv' DELIMITER ',' csv header;

-- eof
