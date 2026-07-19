-- Cria role para a aplicação (não-superusuário)
-- Seguindo o padrão Vinculus de separação entre role de runtime e superusuário

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'lacrei_app') THEN
        CREATE ROLE lacrei_app WITH LOGIN PASSWORD 'lacrei_app';
    END IF;
END
$$;

GRANT USAGE, CREATE ON SCHEMA public TO lacrei_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO lacrei_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO lacrei_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO lacrei_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO lacrei_app;
