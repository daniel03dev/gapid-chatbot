-- Script de inicialización de PostgreSQL para GAPID Chatbot
-- Crea la base de datos y el usuario si no existen

-- Crear el usuario (si no existe)
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'gapid_user') THEN
      CREATE ROLE gapid_user WITH LOGIN PASSWORD 'gapid_password';
   END IF;
END
$do$;

-- Asignar privilegios al usuario
ALTER ROLE gapid_user CREATEDB;

-- Crear la base de datos con el propietario correcto
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'gapid_db') THEN
      CREATE DATABASE gapid_db OWNER gapid_user;
   END IF;
END
$do$;

-- Conceder todos los privilegios en la base de datos
GRANT ALL PRIVILEGES ON DATABASE gapid_db TO gapid_user;

-- Conectar a la base de datos y conceder privilegios en el esquema public
\c gapid_db;

GRANT ALL PRIVILEGES ON SCHEMA public TO gapid_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO gapid_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO gapid_user;
