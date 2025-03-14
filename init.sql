# ilps-auth-service database
CREATE USER service_auth WITH PASSWORD "password123";
CREATE DATABASE auth;
ALTER DATABASE auth OWNER TO service_auth;