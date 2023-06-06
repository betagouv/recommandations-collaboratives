--
-- some data and stats for activity by advisors and staff
--
--
-- create temporary table for notes of interest
CREATE TEMPORARY TABLE interesting_notes AS
SELECT
	ROW_NUMBER() OVER () AS id,
	site_id AS site,
	'note' AS type,
	n.public AS public,
	n.created_on AS creation,
	n.updated_on AS modification,
	p.name AS projet,
	u.email AS auteurice,
	g.group_id AS categorie
FROM
	projects_note n
	INNER JOIN projects_project p ON n.project_id = p.id
	INNER JOIN auth_user u ON n.created_by_id = u.id
	INNER JOIN auth_user_groups g ON u.id = g.user_id
WHERE
	p.exclude_stats = 'f'
	AND g.group_id IN (16, 18) -- staff or advisor
ORDER BY
	n.created_on;

--
-- create temporary table for notes of interest stats
CREATE TEMPORARY TABLE interesting_notes_stats AS
SELECT
	extract(year FROM creation) AS year,
	extract(month FROM creation) AS month,
	categorie,
	count(id)
FROM
	interesting_notes
GROUP BY
	extract(year FROM creation),
	extract(month FROM creation),
	categorie
ORDER BY
	year,
	month,
	categorie ASC;

--
-- notes
\copy (select * from interesting_notes) TO '/tmp/notes.csv' WITH CSV HEADER;
--
-- summary per month
\copy (select * from interesting_notes_stats) TO '/tmp/notes-stats.csv' WITH CSV HEADER;
--
-- temporary table for tasks of interest
CREATE TEMPORARY TABLE interesting_tasks AS
SELECT
	ROW_NUMBER() OVER () AS id,
	n.site_id AS site,
	'action' AS type,
	n.public AS public,
	n.created_on AS creation,
	n.updated_on AS modification,
	p.name AS projet,
	u.email AS auteurice,
	g.group_id AS categorie
FROM
	projects_task n
	INNER JOIN projects_project p ON n.project_id = p.id
	INNER JOIN auth_user u ON n.created_by_id = u.id
	INNER JOIN auth_user_groups g ON g.user_id = u.id
WHERE
	p.exclude_stats = 'f'
	AND g.group_id IN (16, 18) -- staff or advisor
ORDER BY
	n.created_on;

--
-- temporary table for tasks of interest stats
CREATE TEMPORARY TABLE interesting_tasks_stats AS
SELECT
	extract(year FROM creation) AS year,
	extract(month FROM creation) AS month,
	categorie,
	count(id)
FROM
	interesting_tasks
GROUP BY
	extract(year FROM creation),
	extract(month FROM creation),
	categorie
ORDER BY
	year,
	month,
	categorie ASC;

--
-- fetching tasks
\copy (select * from interesting_tasks) TO '/tmp/reco.csv' WITH CSV HEADER;
--
-- summary per month
\copy (select * from interesting_tasks_stats) TO '/tmp/reco-stats.csv' WITH CSV HEADER;
--
-- temporary table of comments of interest
CREATE TEMPORARY TABLE interesting_comments AS
SELECT
	ROW_NUMBER() OVER () AS id,
	'commentaire' AS type,
	NULL AS public,
	tf.timestamp AS creation,
	NULL AS modification,
	p.name AS projet,
	u.email AS auteurice,
	g.group_id AS categorie
FROM
	projects_taskfollowup tf
	INNER JOIN projects_task t ON tf.task_id = t.id
	INNER JOIN projects_project p ON t.project_id = p.id
	INNER JOIN auth_user u ON tf.who_id = u.id
	INNER JOIN auth_user_groups g ON g.user_id = u.id
WHERE
	p.exclude_stats = 'f'
	AND g.group_id IN (16, 18) -- staff or advisor
ORDER BY
	tf.timestamp ASC;

--
-- temporary table of comments of interest stats
CREATE TEMPORARY TABLE interesting_comments_stats AS
SELECT
	extract(year FROM creation) AS year,
	extract(month FROM creation) AS month,
	categorie,
	count(id)
FROM
	interesting_comments
GROUP BY
	extract(year FROM creation),
	extract(month FROM creation),
	categorie
ORDER BY
	year,
	month,
	categorie ASC;

--
-- fetching tasks.comments
\copy (select * from interesting_comments) TO '/tmp/commentaires.csv' WITH CSV HEADER;
--
-- summary per month
\copy (select * from interesting_comments_stats) TO '/tmp/commentaires-stats.csv' WITH CSV HEADER;
--
-- cleanup (should be auto on end of connection)
DROP TABLE interesting_comments;

DROP TABLE interesting_comments_stats;

DROP TABLE interesting_tasks;

DROP TABLE interesting_tasks_stats;

DROP TABLE interesting_notes;

DROP TABLE interesting_notes_stats;

-- eof
