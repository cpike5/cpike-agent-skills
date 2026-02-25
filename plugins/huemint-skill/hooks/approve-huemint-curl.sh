#!/bin/bash
set -euo pipefail

input=$(cat)

# Auto-approve curl requests to the Huemint API
if echo "$input" | grep -q 'api\.huemint\.com'; then
  echo '{"continue":true,"hookSpecificOutput":{"permissionDecision":"allow"},"systemMessage":"Auto-approved Huemint API request"}'
  exit 0
fi

# Not a Huemint request — don't interfere
echo '{"continue":true}'
exit 0
