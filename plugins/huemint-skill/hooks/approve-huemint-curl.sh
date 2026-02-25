#!/bin/bash
set -euo pipefail

input=$(cat)

# Auto-approve curl requests to the Huemint API
if echo "$input" | grep -q 'api\.huemint\.com'; then
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"Huemint API request auto-approved by plugin"}}'
  exit 0
fi

# Not a Huemint request — pass through
exit 0
