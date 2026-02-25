#!/bin/bash

input=$(cat)

# Auto-approve curl requests to the Huemint API
if [[ "$input" == *"api.huemint.com"* ]]; then
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"Huemint API request auto-approved by plugin"}}'
fi

exit 0
