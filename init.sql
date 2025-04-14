-- ilps-service-auth database creation
CREATE USER service_auth WITH PASSWORD 'password123';
CREATE DATABASE auth;
ALTER DATABASE auth OWNER TO service_auth;

-- ilps-service-texts database creation
CREATE USER service_texts WITH PASSWORD 'password123';
CREATE DATABASE texts;
ALTER DATABASE texts OWNER TO service_texts;

-- ilps-service-task-manager database creation
CREATE USER service_task_manager WITH PASSWORD 'password123';
CREATE DATABASE tasks;
ALTER DATABASE tasks OWNER TO service_task_manager;