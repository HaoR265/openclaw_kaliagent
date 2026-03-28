#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
  shift
fi

SOURCE_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_ROOT="${KALICLAW_ROOT:-$HOME/.kaliclaw}"
TARGET_CONFIG="${KALICLAW_CONFIG_BASENAME:-kaliclaw.json}"
LEGACY_CONFIG="openclaw.json"
RUNTIME_DIR="$TARGET_ROOT/events/runtime"
LOCAL_BIN_DIR="${KALICLAW_LOCAL_BIN_DIR:-$HOME/.local/bin}"
LOCAL_BIN_LINK="$LOCAL_BIN_DIR/kaliclaw"

say() {
  printf '[migrate] %s\n' "$1"
}

dry() {
  printf '[dry-run] %s\n' "$1"
}

if [[ ! -d "$SOURCE_ROOT" ]]; then
  printf '[migrate] source root not found: %s\n' "$SOURCE_ROOT" >&2
  exit 1
fi

say "source root: $SOURCE_ROOT"
say "target root: $TARGET_ROOT"

if [[ "$SOURCE_ROOT" != "$TARGET_ROOT" ]]; then
  if [[ "$DRY_RUN" == "1" ]]; then
    dry "mkdir -p $TARGET_ROOT"
    dry "rsync -a --exclude .git/index.lock --exclude dashboard-ui/node_modules/ --exclude node_modules/ --exclude __pycache__/ --exclude .venv/ --exclude events/runtime/*.db-shm --exclude events/runtime/*.db-wal $SOURCE_ROOT/ $TARGET_ROOT/"
  else
    mkdir -p "$TARGET_ROOT"
    rsync -a --exclude ".git/index.lock" --exclude "dashboard-ui/node_modules/" --exclude "node_modules/" --exclude "__pycache__/" --exclude ".venv/" --exclude "events/runtime/*.db-shm" --exclude "events/runtime/*.db-wal" "$SOURCE_ROOT/" "$TARGET_ROOT/"
  fi
else
  say "source and target are identical; will only normalize config/db names"
fi

if [[ "$DRY_RUN" == "1" ]]; then
  dry "mkdir -p $RUNTIME_DIR"
else
  mkdir -p "$RUNTIME_DIR"
fi

if [[ -f "$TARGET_ROOT/events/runtime/openclaw.db" && ! -f "$TARGET_ROOT/events/runtime/kaliclaw.db" ]]; then
  if [[ "$DRY_RUN" == "1" ]]; then
    dry "cp $TARGET_ROOT/events/runtime/openclaw.db $TARGET_ROOT/events/runtime/kaliclaw.db"
    [[ -f "$TARGET_ROOT/events/runtime/openclaw.db-wal" ]] && dry "cp $TARGET_ROOT/events/runtime/openclaw.db-wal $TARGET_ROOT/events/runtime/kaliclaw.db-wal"
    [[ -f "$TARGET_ROOT/events/runtime/openclaw.db-shm" ]] && dry "cp $TARGET_ROOT/events/runtime/openclaw.db-shm $TARGET_ROOT/events/runtime/kaliclaw.db-shm"
  else
    cp "$TARGET_ROOT/events/runtime/openclaw.db" "$TARGET_ROOT/events/runtime/kaliclaw.db"
    [[ -f "$TARGET_ROOT/events/runtime/openclaw.db-wal" ]] && cp "$TARGET_ROOT/events/runtime/openclaw.db-wal" "$TARGET_ROOT/events/runtime/kaliclaw.db-wal"
    [[ -f "$TARGET_ROOT/events/runtime/openclaw.db-shm" ]] && cp "$TARGET_ROOT/events/runtime/openclaw.db-shm" "$TARGET_ROOT/events/runtime/kaliclaw.db-shm"
  fi
fi

MIGRATION_CMD=(python3 "$TARGET_ROOT/update_workspaces.py")
if [[ "$DRY_RUN" == "1" ]]; then
  MIGRATION_CMD+=(--dry-run)
fi
if [[ -f "$TARGET_ROOT/$LEGACY_CONFIG" && ! -f "$TARGET_ROOT/$TARGET_CONFIG" ]]; then
  if [[ "$DRY_RUN" == "1" ]]; then
    dry "KALICLAW_ROOT=$TARGET_ROOT KALICLAW_CONFIG_BASENAME=$TARGET_CONFIG KALICLAW_SOURCE_CONFIG_BASENAME=$LEGACY_CONFIG ${MIGRATION_CMD[*]}"
  else
    KALICLAW_ROOT="$TARGET_ROOT" KALICLAW_CONFIG_BASENAME="$TARGET_CONFIG" KALICLAW_SOURCE_CONFIG_BASENAME="$LEGACY_CONFIG" "${MIGRATION_CMD[@]}"
  fi
else
  if [[ "$DRY_RUN" == "1" ]]; then
    dry "KALICLAW_ROOT=$TARGET_ROOT KALICLAW_CONFIG_BASENAME=$TARGET_CONFIG ${MIGRATION_CMD[*]}"
  else
    KALICLAW_ROOT="$TARGET_ROOT" KALICLAW_CONFIG_BASENAME="$TARGET_CONFIG" "${MIGRATION_CMD[@]}"
  fi
fi

if [[ "$DRY_RUN" == "1" ]]; then
  dry "mkdir -p $LOCAL_BIN_DIR"
  dry "ln -sfn $TARGET_ROOT/kaliclaw $LOCAL_BIN_LINK"
else
  mkdir -p "$LOCAL_BIN_DIR"
  ln -sfn "$TARGET_ROOT/kaliclaw" "$LOCAL_BIN_LINK"
fi

say "migration report"
if [[ "$DRY_RUN" == "1" ]]; then
  printf '  - dry-run only; no files changed\n'
else
  printf '  - target root prepared: %s\n' "$TARGET_ROOT"
  printf '  - default config target: %s/%s\n' "$TARGET_ROOT" "$TARGET_CONFIG"
  printf '  - local CLI link: %s\n' "$LOCAL_BIN_LINK"
fi

printf '\nRollback hints:\n'
printf '  1. remove the new root if needed: rm -rf %q\n' "$TARGET_ROOT"
printf '  2. remove the CLI link if created: rm -f %q\n' "$LOCAL_BIN_LINK"
printf '  3. continue using legacy root: export KALICLAW_ROOT=%q\n' "$HOME/.openclaw"
printf '  4. continue using legacy config: export KALICLAW_CONFIG_PATH=%q\n' "$HOME/.openclaw/openclaw.json"
