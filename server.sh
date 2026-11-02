#!/usr/bin/env bash
# Start everything for local testing: the staging BOINC server (with its work generator,
# validator and assimilator), the BOINC client, and the website on http://127.0.0.1:8080/.
# Ctrl+C stops only the website; the BOINC server and client keep running.
set -euo pipefail
cd "$(dirname "$0")"

# 1. Staging BOINC server: containers, daemons and periodic tasks (incl. the work generator).
# Through up.sh, never a bare "docker compose up": without up.sh's settings (PROJECT=nuclear)
# compose recreates the server as the default "boincserver" project, which breaks staging.
STAGING_HOST=192.168.1.174 bash server/staging/up.sh   # LAN address of this computer (hostname -I)

# 2. BOINC client (a system service; asks for your password if it is not running).
systemctl is-active --quiet boinc-client || sudo systemctl start boinc-client

echo "BOINC server: http://192.168.1.174:8888/nuclear   Website: http://127.0.0.1:8080/"

# 3. Website and 3D viewer (stays in the foreground).
NAH_API_PG_DSN="dbname=nuclear" NAH_SCIENCE_DIR=~/nah-science python3 scripts/serve.py 8080
