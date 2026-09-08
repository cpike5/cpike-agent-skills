#!/bin/bash
# SessionStart hook for a Node/TypeScript project on Claude Code on the web.
#
# Copy to .claude/hooks/session-start.sh and chmod +x.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

export CI=1
export npm_config_fund=false
export npm_config_audit=false

# Honour .nvmrc / package.json engines if the image ships nvm.
if [ -f .nvmrc ] && command -v nvm >/dev/null 2>&1; then
  nvm install && nvm use
fi

node --version
npm --version

# `npm ci` needs a lockfile and wipes node_modules; fall back to install when
# the repo has no lockfile committed.
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo 'export CI=1'
    echo 'export npm_config_fund=false'
  } >> "$CLAUDE_ENV_FILE"
fi

echo "Session start hook complete."
