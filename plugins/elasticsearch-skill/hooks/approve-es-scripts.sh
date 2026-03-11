#!/bin/bash

input=$(cat)

# Auto-approve calls to es-* and kibana-* wrapper scripts
if [[ "$input" == *"/scripts/es-"* ]] || [[ "$input" == *"/scripts/kibana-"* ]]; then
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"ES/Kibana API script auto-approved by plugin"}}'
fi

exit 0
