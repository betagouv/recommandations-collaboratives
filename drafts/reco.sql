--
-- stats on reco usage
COPY (
    SELECT
        t.id AS reco,
        t.created_on AS quand,
        u.username AS qui,
        r.id,
        r.title AS quoi
    FROM
        projects_task AS t
    LEFT JOIN auth_user AS u ON t.created_by_id = u.id
    LEFT JOIN resources_resource AS r ON t.resource_id = r.id
    LEFT JOIN projects_project AS p ON t.project_id = p.id
WHERE
    p.exclude_stats = 'f'
ORDER BY
    t.created_on)
TO '/tmp/reco.csv' DELIMITER ',' csv header;

-- eof
