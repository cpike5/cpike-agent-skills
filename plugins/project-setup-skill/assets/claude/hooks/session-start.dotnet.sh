#!/bin/bash
# SessionStart hook for Claude Code on the web: installs a .NET SDK and restores
# NuGet packages so build/test work in remote sessions.
#
# Copy to .claude/hooks/session-start.sh and chmod +x. Replace <SolutionPath>.
#
# Why apt and not dotnet-install.sh: the web sandbox's network policy blocks
# builds.dotnet.microsoft.com (which dotnet-install.sh / dot.net fetch from), so
# the official installer script cannot reach its payload. The Ubuntu archive and
# api.nuget.org are reachable, so apt + NuGet restore is the path that works.
#
# Why a newer SDK than the target framework: once a .NET version goes EOL it
# leaves both the Ubuntu archive and packages.microsoft.com. A newer SDK still
# builds the older TFM (targeting packs restore from NuGet), and
# DOTNET_ROLL_FORWARD=Major lets the older test hosts run on the newer runtime.
set -euo pipefail

# Only needed in remote (web) sessions; local machines manage their own SDK.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_NOLOGO=1
export DOTNET_ROLL_FORWARD=Major
export DEBIAN_FRONTEND=noninteractive

# Idempotent: the container image may already carry a usable SDK cached from a
# previous session, and reinstalling costs a minute of every session start.
if ! dotnet --list-sdks 2>/dev/null | grep -qE '^(9|[1-9][0-9])\.'; then
  echo "Installing dotnet-sdk-10.0 via apt..."
  # Blocked PPAs in the sandbox make apt-get update return warnings; the Ubuntu
  # archive indexes still fetch, so don't let `set -e` kill the hook over it.
  apt-get update || true
  apt-get install -y dotnet-sdk-10.0
fi

dotnet --version

# Hook processes don't share a shell with the session. CLAUDE_ENV_FILE is how
# exports survive into the tool calls that follow.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo 'export DOTNET_CLI_TELEMETRY_OPTOUT=1'
    echo 'export DOTNET_NOLOGO=1'
    echo 'export DOTNET_ROLL_FORWARD=Major'
  } >> "$CLAUDE_ENV_FILE"
fi

# Restore up front so the first build of the session isn't a cold restore.
dotnet restore "${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}/src/<AppName>.sln"

echo "Session start hook complete."
