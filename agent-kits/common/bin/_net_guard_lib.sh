#!/usr/bin/env bash
set -euo pipefail

REAL_IW="/usr/sbin/iw"
REAL_NMCLI="/usr/bin/nmcli"

get_connected_wifi() {
  "$REAL_NMCLI" -t -f DEVICE,TYPE,STATE dev status 2>/dev/null | awk -F: '$2=="wifi" && $3 ~ /connected|已连接/ {print $1; exit}'
}

is_usb_iface() {
  local iface="$1"
  local devpath
  devpath="$(readlink -f "/sys/class/net/$iface/device" 2>/dev/null || true)"
  [[ -n "$devpath" && "$devpath" == *"/usb"* ]]
}

get_usb_wifi_iface() {
  local i
  for i in /sys/class/net/*; do
    i="$(basename "$i")"
    [[ "$i" == "lo" ]] && continue
    "$REAL_IW" dev "$i" info >/dev/null 2>&1 || continue
    if is_usb_iface "$i"; then
      echo "$i"
      return 0
    fi
  done
  return 1
}

get_usb_phy() {
  local iface="${1:-}"
  [[ -z "$iface" ]] && iface="$(get_usb_wifi_iface || true)"
  [[ -z "$iface" ]] && return 1
  "$REAL_IW" dev 2>/dev/null | awk -v target="$iface" '
    /^phy#/ {phy=$1; sub(/^phy#/, "", phy)}
    $1=="Interface" && $2==target {print "phy" phy; exit}
  '
}

get_monitor_iface() {
  "$REAL_IW" dev 2>/dev/null | awk '
    /^Interface/ {iface=$2}
    /type monitor/ {print iface; exit}
  '
}

deny() {
  echo "[net-guard] DENY: $*" >&2
  exit 126
}
