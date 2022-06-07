--
-- stats of project activity
--
-- add creation date of project
-- add creation date of first task
-- count followup from the project members
--
COPY (
    SELECT
        id,
        name AS project,
        to_char(created, 'dd-mm-YYYY') AS creation,
        to_char(max(FIRST), 'dd-mm-YYYY') AS premiere_reco,
        sum(reco) AS reco,
        sum(notes) AS notes,
        sum(rappels) AS rappels,
        sum(commentaires) AS commentaires
    FROM ((
            SELECT
                p.id AS id,
                p.name AS name,
                p.created_on AS created,
                min(t.created_on) AS first,
                0 AS reco,
                0 AS notes,
                0 AS rappels,
                0 AS commentaires
            FROM
                projects_project AS p
            LEFT JOIN projects_task AS t ON p.id = t.project_id
        WHERE
            p.exclude_stats = 'f'
            AND p.deleted IS NULL
        GROUP BY
            p.id,
            p.name)
    UNION (
        SELECT
            p.id AS id,
            p.name AS name,
            p.created_on AS created,
            NULL AS first,
            count(t.id) AS reco,
            0 AS notes,
            0 AS rappels,
            0 AS commentaires
        FROM
            projects_project AS p
        LEFT JOIN projects_task AS t ON p.id = t.project_id
    WHERE
        p.exclude_stats = 'f'
        AND p.deleted IS NULL
        AND t.status BETWEEN 1 AND 3
    GROUP BY
        p.id,
        p.name)
UNION (
    SELECT
        p.id AS id,
        p.name AS name,
        p.created_on AS created,
        NULL AS first,
        0 AS reco,
        count(n.id) AS notes,
        0 AS rappels,
        0 AS commentaires
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
        AND p.deleted IS NULL
    GROUP BY
        p.id,
        p.name)
UNION (
    SELECT
        p.id AS id,
        p.name AS name,
        p.created_on AS created,
        NULL AS first,
        0 AS reco,
        count(n.id) AS notes,
        0 AS rappels,
        0 AS commentaires
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
        AND p.deleted IS NULL
    GROUP BY
        p.id,
        p.name)
UNION (
    SELECT
        p.id AS id,
        p.name AS name,
        p.created_on AS created,
        NULL AS first,
        0 AS reco,
        0 AS notes,
        0 AS rappels,
        count(f.id) AS commentaires
    FROM
        projects_project AS p
    RIGHT JOIN projects_task AS t ON p.id = t.project_id
    RIGHT JOIN projects_taskfollowup AS f ON t.id = f.task_id
WHERE
    p.exclude_stats = 'f'
    AND p.deleted IS NULL
    AND t.status BETWEEN 1 AND 3
    AND f.who_id NOT IN ( -- who pas un switchtender / prendre dans les acteurs
        SELECT
            s.user_id
        FROM projects_project_switchtenders AS s
        WHERE
            s.id = p.id)
GROUP BY
    p.id,
    p.name)) AS stats
GROUP BY
    id,
    name,
    creation
ORDER BY
    id)
TO '/tmp/stats.csv' DELIMITER ',' csv header;

-- eof
