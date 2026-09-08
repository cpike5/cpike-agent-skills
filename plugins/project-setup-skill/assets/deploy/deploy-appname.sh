#!/bin/bash
# /usr/local/bin/deploy-<appname>.sh
#
# Pulls the image tag currently referenced by /opt/$APP/docker-compose.yml and
# restarts the stack. Idempotent: safe to run when nothing has changed, and
# causes no downtime when the pulled image is unchanged.
#
# Install:
#   sudo install -m 755 deploy-appname.sh /usr/local/bin/deploy-<appname>.sh
#   sudo sed -i 's/^APP=.*/APP=myapp/' /usr/local/bin/deploy-<appname>.sh
#
# Run:
#   sudo deploy-<appname>.sh
#
# Rollback is not handled here on purpose: set APP_TAG to the last good version
# in /opt/$APP/.env and re-run this script.
set -euo pipefail

# The only line to edit. Kept as a variable rather than a literal <appname>
# placeholder so the script is valid shell before it is customised.
APP=changeme

cd "/opt/$APP"

# --quiet suppresses per-layer progress; errors still surface. `set -e` matters
# here: without it a failed pull is followed by `up -d` restarting the stack on
# the OLD image and reporting success.
docker compose pull --quiet

# Only recreates containers whose image actually changed.
docker compose up -d

# Each deploy leaves the previous image untagged. On a small VPS these
# accumulate until the disk fills, which takes the database down with it.
docker image prune -f
