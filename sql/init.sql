--
-- create a database for a django project

-- Create the dedicated database
CREATE DATABASE urbanvitaliz;

-- Create the dedicated user
CREATE USER urbanvitaliz WITH PASSWORD 'urbanvitaliz';

-- grant privileges to dedicated user for creating things
ALTER USER "urbanvitaliz" CREATEDB ;
GRANT ALL PRIVILEGES ON DATABASE "urbanvitaliz" to "urbanvitaliz";

-- Connect to the database
\connect urbanvitaliz;

-- even on pg 15 stay on unsafe usage of public schema
GRANT ALL PRIVILEGES ON SCHEMA public TO urbanvitaliz;
ALTER SCHEMA public OWNER TO urbanvitaliz;

-- Create a new schema with dedicated user as owner for safe usage
CREATE SCHEMA urbanvitaliz AUTHORIZATION urbanvitaliz;

-- Set some settings as recommended by the Django documentation
ALTER ROLE urbanvitaliz SET client_encoding TO 'utf8';
ALTER ROLE urbanvitaliz SET default_transaction_isolation TO 'read committed';
ALTER ROLE urbanvitaliz SET timezone TO 'UTC';

-- eof
