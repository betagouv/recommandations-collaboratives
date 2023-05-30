CREATE DATABASE "urbanvitaliz" ;
CREATE USER "urbanvitaliz" WITH PASSWORD 'urbanvitaliz';
GRANT ALL PRIVILEGES ON DATABASE "urbanvitaliz" to "urbanvitaliz";
ALTER USER "urbanvitaliz" CREATEDB ;

create extension postgis ;
create extension postgis_topology ;
