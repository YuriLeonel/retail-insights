-- Initialize the retail insights database
-- This script runs when the PostgreSQL container starts for the first time
-- Create database if it doesn't exist (this is handled by POSTGRES_DB env var)
-- But we can add any additional setup here
-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Set timezone
SET timezone = 'UTC';
-- Create any additional schemas or configurations
-- The main tables will be created by SQLAlchemy migrations