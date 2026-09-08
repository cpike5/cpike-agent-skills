#!/bin/bash
# scripts/test-db.sh — throwaway Postgres test database.
#
# The fallback for environments that have the docker CLI but no daemon (some
# agent sandboxes), where Testcontainers cannot start. Where Docker works,
# prefer Testcontainers and skip this.
#
#   ./scripts/test-db.sh up       # start cluster, create a fresh db, print conn string
#   ./scripts/test-db.sh down     # drop the db named in .test-db-name
#   ./scripts/test-db.sh reset    # down + up
#
# Wire it up:
#   export TEST_DB_CONNECTION="$(./scripts/test-db.sh up)"
#   dotnet test
#
# The test fixture should read TEST_DB_CONNECTION and fall back to
# Testcontainers when it is unset, so no test knows which mechanism it got.
set -euo pipefail

DB_USER="${TEST_DB_USER:-postgres}"
DB_PASSWORD="${TEST_DB_PASSWORD:-postgres}"
DB_HOST="${TEST_DB_HOST:-localhost}"
DB_PORT="${TEST_DB_PORT:-5432}"

# Records the generated database name so `down` can drop the right one.
NAME_FILE="$(cd "$(dirname "$0")/.." && pwd)/.test-db-name"

# psql refuses to run as root, so route through the postgres system user when
# we are root. Locally, run as yourself and this is a no-op.
psql_as_super() {
  if [ "$(id -u)" -eq 0 ] && id postgres >/dev/null 2>&1; then
    su postgres -c "psql -v ON_ERROR_STOP=1 $*"
  else
    psql -v ON_ERROR_STOP=1 "$@"
  fi
}

ensure_cluster() {
  if pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; then
    return
  fi
  echo "Starting PostgreSQL..." >&2
  service postgresql start >/dev/null 2>&1 || pg_ctlcluster 16 main start || true

  # Wait for readiness rather than sleeping a guessed interval.
  for _ in $(seq 1 30); do
    pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1 && return
    sleep 1
  done
  echo "PostgreSQL did not become ready on $DB_HOST:$DB_PORT" >&2
  exit 1
}

up() {
  ensure_cluster

  # Idempotent: a re-run on an already-configured cluster must not fail.
  psql_as_super -c "ALTER USER $DB_USER PASSWORD '$DB_PASSWORD';" >/dev/null

  # Unique name per run: two suites (or a stale one) never share state, and a
  # crashed run leaves no database that a later run silently inherits.
  local db="test_$(date +%s)_$$"
  psql_as_super -c "CREATE DATABASE $db OWNER $DB_USER;" >/dev/null
  echo "$db" > "$NAME_FILE"

  # Only the connection string goes to stdout, so the caller can capture it.
  echo "Host=$DB_HOST;Port=$DB_PORT;Database=$db;Username=$DB_USER;Password=$DB_PASSWORD"
}

down() {
  [ -f "$NAME_FILE" ] || { echo "No $NAME_FILE; nothing to drop." >&2; return 0; }
  local db
  db="$(cat "$NAME_FILE")"

  # WITH (FORCE) terminates lingering connections; without it a leaked
  # DbContext from a crashed run blocks the drop forever.
  psql_as_super -c "DROP DATABASE IF EXISTS $db WITH (FORCE);" >/dev/null
  rm -f "$NAME_FILE"
  echo "Dropped $db" >&2
}

case "${1:-up}" in
  up)    up ;;
  down)  down ;;
  reset) down; up ;;
  *)     echo "usage: $0 {up|down|reset}" >&2; exit 2 ;;
esac
