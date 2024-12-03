#!/bin/bash

# Prerequisites:
# run update_materialized_views from develop
# switch to branch mt-views-refacto
# change METRICS_PREFIX to "metrics_bis" and run update_materialized_views

rm -rf metrics_export
mkdir -p metrics_export

export PGPASSWORD=postgres

PSQL_COMMAND="psql -h localhost -d postgres -U postgres -c"


echo " >> Exporting metrics_urbanvitaliz_fr.projects"

$PSQL_COMMAND "COPY (SELECT created_on,inactive_since,hash,recommandation_count,advisor_count,member_count,public_message_count,public_message_from_members_count,public_message_from_advisors_count,private_message_count,project_topics,crm_annotations_tags,advised_by,commune_insee,status,site_origin,all_sites FROM metrics_urbanvitaliz_fr.projects ORDER BY hash ASC) TO STDOUT WITH CSV HEADER" > metrics_export/metrics_urbanvitaliz_fr_projects.csv

$PSQL_COMMAND "COPY (SELECT created_on,inactive_since,hash,recommandation_count,advisor_count,member_count,public_message_count,public_message_from_members_count,public_message_from_advisors_count,private_message_count,project_topics,crm_annotations_tags,advised_by,commune_insee,status,site_origin,all_sites FROM metrics_bis_urbanvitaliz_fr.projects ORDER BY hash ASC) TO STDOUT WITH CSV HEADER" > metrics_export/metrics_bis_urbanvitaliz_fr_projects.csv


echo " >> Exporting metrics_urbanvitaliz_fr.recommendations"

$PSQL_COMMAND "COPY (SELECT hash,public,project_hash,created_by_hash,created_on,status_name,comment_count,member_comment_count,advisor_comment_count,visited,has_resource,topic_name FROM metrics_urbanvitaliz_fr.recommendations) TO STDOUT WITH CSV HEADER" > metrics_export/metrics_urbanvitaliz_fr_recommendations.csv

$PSQL_COMMAND "COPY (SELECT hash,public,project_hash,created_by_hash,created_on,status_name,comment_count,member_comment_count,advisor_comment_count,visited,has_resource,topic_name FROM metrics_bis_urbanvitaliz_fr.recommendations) TO STDOUT WITH CSV HEADER" > metrics_export/metrics_bis_urbanvitaliz_fr_recommendations.csv


echo " >> Exporting metrics_urbanvitaliz_fr.resources"

$PSQL_COMMAND "COPY (SELECT created_on,updated_on,hash,status_name,created_by_hash FROM metrics_urbanvitaliz_fr.resources ORDER BY hash ASC) TO STDOUT WITH CSV HEADER" > metrics_export/metrics_urbanvitaliz_fr_resources.csv

$PSQL_COMMAND "COPY (SELECT created_on,updated_on,hash,status_name,created_by_hash FROM metrics_bis_urbanvitaliz_fr.resources ORDER BY hash ASC) TO STDOUT WITH CSV HEADER" > metrics_export/metrics_bis_urbanvitaliz_fr_resources.csv


echo " >> Exporting metrics_urbanvitaliz_fr.users"

$PSQL_COMMAND "COPY (SELECT date_joined,last_login,hash,is_advisor,advising_departments,is_site_staff,advisor_scope FROM metrics_urbanvitaliz_fr.users) TO STDOUT WITH CSV HEADER" > metrics_export/metrics_urbanvitaliz_fr_users.csv

$PSQL_COMMAND "COPY (SELECT date_joined,last_login,hash,is_advisor,advising_departments,is_site_staff,advisor_scope FROM metrics_bis_urbanvitaliz_fr.users) TO STDOUT WITH CSV HEADER" > metrics_export/metrics_bis_urbanvitaliz_fr_users.csv


echo " >> Exporting metrics_urbanvitaliz_fr.user_activity"

$PSQL_COMMAND "COPY (SELECT user_hash AS hash,event_name FROM metrics_urbanvitaliz_fr.user_activity ORDER BY hash ASC) TO STDOUT WITH CSV HEADER" > metrics_export/metrics_urbanvitaliz_fr_user_activity.csv

$PSQL_COMMAND "COPY (SELECT hash,event_name FROM metrics_bis_urbanvitaliz_fr.user_activity ORDER BY hash ASC) TO STDOUT WITH CSV HEADER" > metrics_export/metrics_bis_urbanvitaliz_fr_user_activity.csv


# Not ok, some diff
meld metrics_export/metrics_urbanvitaliz_fr_projects.csv metrics_export/metrics_bis_urbanvitaliz_fr_projects.csv

# Ok, no diff
# meld metrics_export/metrics_urbanvitaliz_fr_resources.csv metrics_export/metrics_bis_urbanvitaliz_fr_resources.csv
# meld metrics_export/metrics_urbanvitaliz_fr_recommendations.csv metrics_export/metrics_bis_urbanvitaliz_fr_recommendations.csv
# meld metrics_export/metrics_urbanvitaliz_fr_user_activity.csv metrics_export/metrics_bis_urbanvitaliz_fr_user_activity.csv
# meld metrics_export/metrics_urbanvitaliz_fr_users.csv metrics_export/metrics_bis_urbanvitaliz_fr_users.csv
