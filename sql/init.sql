--
-- create a database for a django project

-- Create the dedicated database
CREATE DATABASE recoco;

-- Create the dedicated user
CREATE USER recoco WITH PASSWORD 'recoco';

-- grant privileges to dedicated user for creating things
ALTER USER "recoco" CREATEDB ;
GRANT ALL PRIVILEGES ON DATABASE "recoco" to "recoco";

-- Connect to the database
\connect recoco;

-- even on pg 15 stay on unsafe usage of public schema
GRANT ALL PRIVILEGES ON SCHEMA public TO recoco;
ALTER SCHEMA public OWNER TO recoco;

-- Create a new schema with dedicated user as owner for safe usage
CREATE SCHEMA recoco AUTHORIZATION recoco;

-- Set some settings as recommended by the Django documentation
ALTER ROLE recoco SET client_encoding TO 'utf8';
ALTER ROLE recoco SET default_transaction_isolation TO 'read committed';
ALTER ROLE recoco SET timezone TO 'UTC';

-- eof
