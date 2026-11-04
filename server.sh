#!/usr/bin/env bash
# Start everything for local testing: the staging BOINC server (with its work generator,
# validator and assimilator), the BOINC client, and the website on http://<this computer's network address>:8080/ (this computer and others on the home network).
# Ctrl+C stops only the website; the BOINC server and client keep running.
set -euo pipefail
cd "$(dirname "$0")"

# 1. Staging BOINC server: containers, daemons and periodic tasks (incl. the work generator).
# Through up.sh, never a bare "docker compose up": without up.sh's settings (PROJECT=nuclear)
# compose recreates the server as the default "boincserver" project, which breaks staging.
# This computer's current home-network address: it changes with the Wi-Fi network, and Docker cannot
# listen on an address the computer no longer has (staging failed to start after a network change).
# up.sh points stored work at the new address; BOINC clients attached at the old one must re-add it.
lan="${STAGING_HOST:-$(bash server/staging/address.sh)}"   # config/staging.conf
if [ "$lan" != 127.0.0.1 ]; then
  wifi=$(nmcli -t -f NAME,TYPE con show --active 2>/dev/null | awk -F: '$2 ~ /wireless|ethernet/ {print $1; exit}')
  echo "Staging and the website will be open to every device on network '${wifi:-unknown}' at $lan."
  echo "Only do this on your own home network (else set address=127.0.0.1 in config/staging.conf)."
  read -r -p "Continue? [y/N] " ok
  [ "$ok" = y ] || [ "$ok" = Y ] || { echo "Stopped."; exit 1; }
fi
STAGING_HOST=$lan bash server/staging/up.sh

# 2. BOINC client (a system service; asks for your password if it is not running).
systemctl is-active --quiet boinc-client || sudo systemctl start boinc-client

echo "BOINC server: http://$lan:8888/nuclear   Website: http://$lan:8080/"

# 3. Website and 3D viewer (stays in the foreground).
# Reads the staging server's science database and files, so it shows every computer and result.
# NAH_WEB_HOST: other PCs on the home network can open the site at this address.
NAH_WEB_HOST=$lan NAH_API_PG_DSN="host=127.0.0.1 port=5433 dbname=nuclear user=postgres" NAH_SCIENCE_DIR="$(bash server/staging/science_dir.sh ~/nah-staging/science)" \
  python3 scripts/serve.py 8080
