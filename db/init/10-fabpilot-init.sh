#!/usr/bin/env bash
# Creates FabPilot roles, databases and schemas. Must run as a PostgreSQL superuser.
#
# - Docker: mounted into /docker-entrypoint-initdb.d, runs once on an empty volume.
# - CI / manual: PGHOST=localhost PGUSER=postgres PGPASSWORD=... FABPILOT_SQL_DIR=./db bash db/init/10-fabpilot-init.sh
#
# Roles (least privilege):
#   fab_loader   owns fab_business; used only by the synthetic data generator
#   fab_reader   SELECT-only on fab_business, sessions forced read-only; used by the agent
#   fabpilot_app owns fabpilot_app (conversations, audit, RAG)
set -euo pipefail

SQL_DIR="${FABPILOT_SQL_DIR:-/fabpilot-db}"
SUPERUSER="${POSTGRES_USER:-${PGUSER:-postgres}}"
psql_su() { psql -v ON_ERROR_STOP=1 --username "$SUPERUSER" "$@"; }

psql_su --dbname postgres \
  -v loader_pw="${FAB_LOADER_PASSWORD:-fab_loader}" \
  -v reader_pw="${FAB_READER_PASSWORD:-fab_reader}" \
  -v app_pw="${FABPILOT_APP_PASSWORD:-fabpilot_app}" <<'SQL'
CREATE ROLE fab_loader   LOGIN PASSWORD :'loader_pw';
CREATE ROLE fab_reader   LOGIN PASSWORD :'reader_pw';
CREATE ROLE fabpilot_app LOGIN PASSWORD :'app_pw';
CREATE DATABASE fab_business OWNER fab_loader;
CREATE DATABASE fabpilot_app OWNER fabpilot_app;
ALTER ROLE fab_reader SET default_transaction_read_only = on;
ALTER ROLE fab_reader   IN DATABASE fab_business SET search_path = fab;
ALTER ROLE fab_loader   IN DATABASE fab_business SET search_path = fab;
ALTER ROLE fabpilot_app IN DATABASE fabpilot_app SET search_path = app, public;
SQL

# Business schema, owned by fab_loader; fab_reader gets SELECT only.
for f in "$SQL_DIR"/business/*.sql; do
  psql_su --dbname fab_business -c "SET ROLE fab_loader" -f "$f"
done
psql_su --dbname fab_business <<'SQL'
REVOKE ALL ON DATABASE fab_business FROM PUBLIC;
GRANT CONNECT ON DATABASE fab_business TO fab_reader;
GRANT USAGE ON SCHEMA fab TO fab_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA fab TO fab_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE fab_loader IN SCHEMA fab GRANT SELECT ON TABLES TO fab_reader;
SQL

# App schema. Extensions need superuser, the rest is owned by fabpilot_app.
psql_su --dbname fabpilot_app -c "CREATE EXTENSION IF NOT EXISTS vector"
psql_su --dbname fabpilot_app -c "REVOKE ALL ON DATABASE fabpilot_app FROM PUBLIC"
for f in "$SQL_DIR"/app/*.sql; do
  psql_su --dbname fabpilot_app -c "SET ROLE fabpilot_app" -f "$f"
done

echo "FabPilot databases initialised."
