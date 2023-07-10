--
-- stats on reco usage

COPY (
    SELECT
        count(t.id) AS total,
        r.id,
        r.title AS quoi
    FROM
        projects_task AS t
    LEFT JOIN resources_resource AS r ON t.resource_id = r.id
    LEFT JOIN projects_project AS p ON t.project_id = p.id
WHERE
    p.exclude_stats = 'f'
GROUP BY
    r.id, r.title
ORDER BY
    total DESC)
TO '/tmp/reco-stats.csv' DELIMITER ',' csv header;

-- eof
