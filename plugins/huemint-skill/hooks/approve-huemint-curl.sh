#!/bin/bash
set -euo pipefail

input=$(cat)

# Auto-approve curl requests to the Huemint API (no jq dependency)
if echo "$input" | grep -q 'api\.huemint\.com'; then
  echo '{"hookSpecificOutput":{"permissionDecision":"allow"}}'
  exit 0
fi

# Not a Huemint request — don't interfere
exit 0
