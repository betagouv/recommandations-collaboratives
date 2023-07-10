--
-- reporting on notes usage
COPY (
    SELECT
        n.created_on AS quand,
        p.name AS projet,
        u.username AS qui,
        n.tags AS tags
    FROM
        projects_note AS n
    LEFT JOIN projects_project AS p ON n.project_id = p.id
    LEFT JOIN auth_user AS u ON n.created_by_id = u.id
WHERE
    p.exclude_stats = 'f'
    AND n.created_by_id IS NOT NULL
    AND n.public = 't'
    AND n.content NOT LIKE '# Demande initiale%'
ORDER BY
    n.created_on)
TO '/tmp/notes.csv' DELIMITER ',' csv header;

-- eof
