#!/bin/bash

input=$(cat)

# Auto-approve calls to es-api and kibana-api wrapper scripts
if [[ "$input" == *"/scripts/es-api"* ]] || [[ "$input" == *"/scripts/kibana-api"* ]]; then
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"ES/Kibana API script auto-approved by plugin"}}'
fi

exit 0
