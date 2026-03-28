#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-${KALICLAW_ROOT:-$HOME/.kaliclaw}}"
CONFIG="$ROOT/${KALICLAW_CONFIG_BASENAME:-kaliclaw.json}"
LEGACY_CONFIG="$ROOT/openclaw.json"
DB="$ROOT/events/runtime/${KALICLAW_DB_BASENAME:-kaliclaw.db}"
LEGACY_DB="$ROOT/events/runtime/openclaw.db"
WRAPPER="$ROOT/kaliclaw"
COMMON_BIN_WRAPPER="$ROOT/agent-kits/common/bin/kaliclaw"

status=0
check() {
  local path="$1"
  local label="$2"
  if [[ -e "$path" ]]; then
    printf 'OK   %-22s %s\n' "$label" "$path"
  else
    printf 'MISS %-22s %s\n' "$label" "$path"
    status=1
  fi
}

printf 'Kaliclaw runtime check\n'
printf 'root:   %s\n' "$ROOT"
printf 'config: %s\n' "$CONFIG"
printf 'db:     %s\n' "$DB"
printf '\n'

check "$ROOT" root
check "$WRAPPER" wrapper
check "$COMMON_BIN_WRAPPER" common-bin-wrapper
if [[ -e "$CONFIG" ]]; then
  printf 'OK   %-22s %s\n' config "$CONFIG"
elif [[ -e "$LEGACY_CONFIG" ]]; then
  printf 'WARN %-22s legacy fallback %s\n' config "$LEGACY_CONFIG"
else
  printf 'MISS %-22s %s\n' config "$CONFIG"
  status=1
fi
if [[ -e "$DB" ]]; then
  printf 'OK   %-22s %s\n' runtime-db "$DB"
elif [[ -e "$LEGACY_DB" ]]; then
  printf 'WARN %-22s legacy fallback %s\n' runtime-db "$LEGACY_DB"
else
  printf 'MISS %-22s %s\n' runtime-db "$DB"
  status=1
fi
check "$ROOT/dashboard/server.py" dashboard-server
check "$ROOT/update_workspaces.py" workspace-migrator

if [[ -x "$WRAPPER" ]]; then
  printf '\nCLI resolution:\n'
  if KALICLAW_ROOT="$ROOT" KALICLAW_QUIET_COMPAT=1 "$WRAPPER" config file 2>/dev/null; then
    true
  else
    printf 'WARN wrapper exists but `kaliclaw config file` failed\n'
    status=1
  fi
fi

exit "$status"
