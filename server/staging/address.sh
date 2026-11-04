#!/usr/bin/env bash
# Print the staging address from config/staging.conf: a fixed address as written, or for "auto"
# the address of the interface carrying the default route (never a Docker or LXC bridge).
set -euo pipefail
conf="$(cd "$(dirname "$0")/../.." && pwd)/config/staging.conf"
address=$(sed -n 's/^address=//p' "$conf" | tr -d '[:space:]')
case "$address" in
  auto) ip route get 1.1.1.1 | sed -n 's/.* src \([0-9.]*\).*/\1/p' ;;
  "") echo "no address= line in $conf" >&2; exit 1 ;;
  *) echo "$address" ;;
esac
