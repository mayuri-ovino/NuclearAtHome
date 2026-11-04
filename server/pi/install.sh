#!/usr/bin/env bash
# Install the whole Nuclear@Home server natively on a Raspberry Pi 4/5 (Raspberry Pi OS 64-bit,
# bookworm) or any Debian bookworm machine: BOINC server built from source, MariaDB, PostgreSQL,
# Apache (BOINC, port 8888), nginx + gunicorn (website, port 80). The published BOINC Docker images
# are x86-only, hence native. The Pi never runs LAMMPS: it stores and serves volunteers' binaries.
#
# Copy the project to /opt/nuclear-at-home first, including the prebuilt binaries in
# client/app_version/ (git does not hold them):  rsync -a nuclear-at-home/ pi:/opt/nuclear-at-home/
#
# Usage: sudo bash /opt/nuclear-at-home/server/pi/install.sh [--address ADDR] [--test-key]
#   --address   address volunteers use (default: config/staging.conf)
#   --test-key  let BOINC create a signing key on this machine. Private home use only: for anything
#               public, sign offline and put code_sign_public and the .sig files in
#               client/app_version/signed/ (docs/deploy.md); the private key then never exists here.
set -euo pipefail

BOINC_COMMIT=679b7c89d0db3b0f1c190c53686dbb508a9b13be  # the commit boinc-server-docker pins
REPO=/opt/nuclear-at-home
PROJECT=nuclear
USER_NAME=boincadm
HOME_DIR=/home/$USER_NAME
PROJECT_ROOT=$HOME_DIR/projects/$PROJECT
SCIENCE=/srv/nuclear/science
BOINC_SRC=/opt/boinc-src

address=""; test_key=no
while [ $# -gt 0 ]; do
  case "$1" in
    --address) address="$2"; shift 2 ;;
    --test-key) test_key=yes; shift ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
done
[ "$(id -u)" = 0 ] || { echo "run with sudo" >&2; exit 1; }
[ -d "$REPO/client/app_version" ] || { echo "copy the project to $REPO first" >&2; exit 1; }
[ "$(getconf LONG_BIT)" = 64 ] || { echo "needs a 64-bit OS (Raspberry Pi OS 64-bit)" >&2; exit 1; }
signed="$REPO/client/app_version/signed"
if [ ! -f "$signed/code_sign_public" ] && [ "$test_key" = no ]; then
  echo "No offline signatures in $signed. Sign offline (docs/deploy.md), or pass --test-key for private home use." >&2
  exit 1
fi

as_boinc() { runuser -u "$USER_NAME" -- "$@"; }
start_service() {  # systemd on a Pi; plain service scripts in a test container
  if [ -d /run/systemd/system ]; then systemctl enable --now "$1"; else service "$1" start; fi
}
restart_service() {  # picks up a changed config, on a first run or a rerun
  if [ -d /run/systemd/system ]; then systemctl enable "$1"; systemctl restart "$1"
  else service "$1" stop || true; sleep 2; service "$1" start; fi
}

echo "== Packages"
apt-get update -qq
apt-get install -y -qq --no-install-recommends \
  ca-certificates curl cron git iproute2 openssl rsync m4 make g++ dh-autoreconf pkg-config \
  libcurl4-gnutls-dev default-libmysqlclient-dev libssl-dev libzip-dev nlohmann-json3-dev \
  mariadb-server postgresql apache2 libapache2-mod-php php-cli php-mysql php-xml php-gd \
  nginx gunicorn python3 python-is-python3 python3-setuptools python3-dev python3-mysqldb python3-numpy python3-scipy \
  python3-jsonschema python3-psycopg python3-pymysql >/dev/null
[ -n "$address" ] || address=$(bash "$REPO/server/staging/address.sh")
echo "   project address: http://$address:8888/$PROJECT/"

echo "== Users and folders"
id "$USER_NAME" >/dev/null 2>&1 || useradd --create-home --shell /bin/bash "$USER_NAME"
id nah >/dev/null 2>&1 || useradd --system --home "$REPO" --shell /usr/sbin/nologin nah
usermod -aG "$USER_NAME" www-data
chmod g+rx "$HOME_DIR"
mkdir -p "$SCIENCE" "$BOINC_SRC"
chown "$USER_NAME:$USER_NAME" "$SCIENCE" "$BOINC_SRC"
chmod 755 /srv/nuclear "$SCIENCE"

echo "== BOINC server, from source (takes a while on a Pi)"
if [ ! -x "$BOINC_SRC/sched/cgi" ]; then
  as_boinc git -C "$BOINC_SRC" init -q
  as_boinc git -C "$BOINC_SRC" fetch -q --depth 1 https://github.com/BOINC/boinc.git "$BOINC_COMMIT"
  as_boinc git -C "$BOINC_SRC" checkout -q FETCH_HEAD
  # Serial make: parallel builds fail here (libboinc .Tpo race).
  as_boinc bash -c "cd $BOINC_SRC && { ./_autosetup && ./configure --disable-client --disable-manager && make; } > build.log 2>&1" \
    || { tail -20 "$BOINC_SRC/build.log"; exit 1; }
fi

echo "== MariaDB and BOINC project"
start_service mariadb
if [ ! -f "$PROJECT_ROOT/config.xml" ]; then
  db_pass=$(openssl rand -hex 24)   # lives only in the project's config.xml; never printed
  mysql <<SQL
CREATE USER IF NOT EXISTS '$USER_NAME'@'localhost' IDENTIFIED BY '$db_pass';
GRANT ALL ON \`$PROJECT\`.* TO '$USER_NAME'@'localhost';
SQL
  as_boinc mkdir -p "$HOME_DIR/projects"
  ( cd "$BOINC_SRC/tools" && as_boinc env HOME="$HOME_DIR" ./make_project --url_base "http://$address:8888" \
      --db_host localhost --db_user "$USER_NAME" --db_passwd "$db_pass" --no_query \
      --project_root "$PROJECT_ROOT" "$PROJECT" >/dev/null )
  unset db_pass
fi
chmod -R g+w "$PROJECT_ROOT/download" "$PROJECT_ROOT/upload"
mkdir -p "$PROJECT_ROOT/html/stats_archive"; chown "$USER_NAME:$USER_NAME" "$PROJECT_ROOT/html/stats_archive"
chmod 640 "$PROJECT_ROOT/config.xml"
# make_project leaves private keys world-readable; the scheduler (www-data, in the group) needs upload_private.
chmod 640 "$PROJECT_ROOT/keys/upload_private"
[ ! -f "$PROJECT_ROOT/keys/code_sign_private" ] || chmod 600 "$PROJECT_ROOT/keys/code_sign_private"
if [ -f "$signed/code_sign_public" ]; then
  # Offline signing: the public key goes on this machine, and no private code-signing key stays here.
  install -o "$USER_NAME" -m 644 "$signed/code_sign_public" "$PROJECT_ROOT/keys/code_sign_public"
  shred -u "$PROJECT_ROOT/keys/code_sign_private" 2>/dev/null || true
fi

echo "== Apache (BOINC on port 8888)"
grep -q '^Listen 8888' /etc/apache2/ports.conf || echo 'Listen 8888' >> /etc/apache2/ports.conf
sed -i 's/^Listen 80$/# Listen 80: nginx serves the website there/' /etc/apache2/ports.conf
a2enmod -q cgi >/dev/null 2>&1 || a2enmod -q cgid >/dev/null
a2dissite -q 000-default >/dev/null 2>&1 || true
cat > /etc/apache2/sites-available/$PROJECT.conf <<CONF
<VirtualHost *:8888>
    Include $PROJECT_ROOT/$PROJECT.httpd.conf
</VirtualHost>
CONF
a2ensite -q "$PROJECT" >/dev/null
restart_service apache2

echo "== PostgreSQL (science database)"
start_service postgresql
cd /tmp
role_exists() { runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$1'" | grep -q 1; }
role_exists "$USER_NAME" || runuser -u postgres -- createuser "$USER_NAME"
role_exists nah || runuser -u postgres -- createuser nah
if ! runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_database WHERE datname='nuclear'" | grep -q 1; then
  runuser -u postgres -- createdb -O "$USER_NAME" nuclear
  runuser -u postgres -- psql -q -d nuclear -c "CREATE ROLE nah_api NOLOGIN" 2>/dev/null || true
  sed '/^CREATE ROLE nah_api/d' "$REPO/stats/schema.sql" | as_boinc psql -q -d nuclear -v ON_ERROR_STOP=1
  runuser -u postgres -- psql -q -d nuclear -c "GRANT nah_api TO nah"
fi

echo "== App versions, daemons, periodic jobs"
cat > "$PROJECT_ROOT/bin/nah.env" <<ENV
export NAH_PYTHON=python3
export NAH_PG_DSN=dbname=nuclear
export NAH_SCIENCE_DIR=$SCIENCE
export NAH_BOINC_PROJECT_DIR=$PROJECT_ROOT
ENV
chown "$USER_NAME:$USER_NAME" "$PROJECT_ROOT/bin/nah.env"; chmod 600 "$PROJECT_ROOT/bin/nah.env"
as_boinc env PROJECT_ROOT="$PROJECT_ROOT" bash "$REPO/server/staging/install_app.sh"
mysql "$PROJECT" -e "UPDATE app SET n_size_classes = 2 WHERE name = 'nuclear_cascade';"
as_boinc bash -c "cd $PROJECT_ROOT/html/ops && php size_census.php --all_apps" >/dev/null
start_service cron
( crontab -u "$USER_NAME" -l 2>/dev/null | grep -v 'bin/start --cron' || true
  echo "*/5 * * * * cd $PROJECT_ROOT && bin/start --cron" ) | crontab -u "$USER_NAME" -
as_boinc bash -c "cd $PROJECT_ROOT && bin/start" >/dev/null

echo "== Website (nginx + gunicorn on port 80, home-network form of server/nginx_nah.conf)"
awk '/^server \{/ { n++ } n < 2 { print }' "$REPO/server/nginx_nah.conf" \
  | sed -e 's/listen 443 ssl;/listen 80;/' -e '/http2 on;/d' -e '/ssl_certificate/d' \
        -e '/Strict-Transport-Security/d' -e 's/server_name stats.example.org;.*/server_name _;/' \
  > /etc/nginx/sites-available/nuclear
ln -sf /etc/nginx/sites-available/nuclear /etc/nginx/sites-enabled/nuclear
rm -f /etc/nginx/sites-enabled/default
nginx -t -q
restart_service nginx
if [ -d /run/systemd/system ]; then
  cp "$REPO/server/nah-api.service" /etc/systemd/system/nah-api.service
  systemctl daemon-reload; systemctl enable --now nah-api
else  # test container: no systemd
  runuser -u nah -- env NAH_API_PG_DSN="dbname=nuclear user=nah" NAH_SCIENCE_DIR="$SCIENCE" \
    bash -c "cd $REPO && nohup gunicorn --bind 127.0.0.1:8000 --workers 2 stats.api:application >/tmp/nah-api.log 2>&1 &"
fi

echo
echo "Done."
echo "  BOINC project: http://$address:8888/$PROJECT/   (BOINC Manager: Tools, Add project)"
echo "  Website:       http://$address/"
echo "  Work generator is off until you run:  bash $REPO/server/pi/autogen.sh on"
[ "$test_key" = yes ] && echo "  Signing key: created on this machine (--test-key). Private home use only."
exit 0
