--
-- create a database for a django project

-- Create the database for the application
CREATE DATABASE urbanvitaliz;

-- Create the dedicated user
CREATE USER urbanvitaliz WITH PASSWORD 'urbanvitaliz';

-- grant privileges for creating things
ALTER USER "urbanvitaliz" CREATEDB ;
GRANT ALL PRIVILEGES ON DATABASE "urbanvitaliz" to "urbanvitaliz";

-- Connect to the database
\connect urbanvitaliz;

-- Create a new schema dedicated user as owner
CREATE SCHEMA urbanvitaliz AUTHORIZATION urbanvitaliz;

-- Set some settings as recommended by the Django documentation
ALTER ROLE urbanvitaliz SET client_encoding TO 'utf8';
ALTER ROLE urbanvitaliz SET default_transaction_isolation TO 'read committed';
ALTER ROLE urbanvitaliz SET timezone TO 'UTC';


-- eof
