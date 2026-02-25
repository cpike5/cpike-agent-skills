#!/bin/bash
set -euo pipefail

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# Auto-approve curl/fetch requests to the Huemint API
if echo "$command" | grep -qE 'curl\s.*api\.huemint\.com'; then
  echo '{"hookSpecificOutput":{"permissionDecision":"allow"}}'
  exit 0
fi

# Not a Huemint curl — don't interfere
exit 0
