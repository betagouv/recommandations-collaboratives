--
-- stats of project activity
copy (
SELECT
    id,
    name,
    sum(reco) AS reco,
    sum(notes) AS notes,
    sum(rappels) AS rappels
FROM ((
        SELECT
            p.id AS id,
            p.name AS name,
            count(t.id) AS reco,
            0 AS notes,
            0 AS rappels
        FROM
            projects_project AS p
        LEFT JOIN projects_task AS t ON p.id = t.project_id
            AND t.status BETWEEN 1 AND 3
    WHERE
        p.exclude_stats = 'f'
    GROUP BY
        p.id,
        p.name)
UNION (
    SELECT
        p.id AS id,
        p.name AS name,
        0 AS reco,
        count(n.id) AS notes,
        0 AS rappels
    FROM
        projects_project AS p
    LEFT JOIN projects_note AS n ON p.id = n.project_id
        AND n.public = 't'
        AND n.created_by_id NOT IN (
            SELECT
                s.user_id
            FROM
                projects_project_switchtenders AS s
        WHERE
            s.id = p.id)
    WHERE
        p.exclude_stats = 'f'
    GROUP BY
        p.id,
        p.name)
UNION (
    SELECT
        p.id AS id,
        p.name AS name,
        0 AS reco,
        0 AS notes,
        count(r.id) AS rappels
    FROM
        projects_project AS p
    RIGHT JOIN projects_task AS t ON p.id = t.project_id
    RIGHT JOIN reminders_mail AS r ON t.id = r.object_id
WHERE
    p.exclude_stats = 'f'
    AND r.origin = 2
    AND r.content_type_id = 10
GROUP BY
    p.id,
    p.name)) AS stats
GROUP BY
    id,
    name
ORDER BY
    id
) to '/tmp/stats.csv' delimiter ',' csv header ;
-- eof
