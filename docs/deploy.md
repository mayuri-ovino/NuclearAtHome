# Hosting the Nuclear@Home website

The site is static files (`viewer/`) plus a read-only JSON API (`stats/api.py`) reading
PostgreSQL. The same code runs on your laptop and on a Raspberry Pi.

| | Laptop (development) | Raspberry Pi (permanent) |
|---|---|---|
| Web server | `scripts/serve.py` (Python standard library) | nginx (`server/nginx_nah.conf`) |
| API | inside `serve.py` | gunicorn (`server/nah-api.service`) |
| Database | PostgreSQL | PostgreSQL |

## 1. Laptop

One-time setup:

```bash
sudo apt install python3-psycopg
sudo -u postgres createuser --superuser $USER
createdb nuclear
psql -d nuclear -f stats/schema.sql
mkdir -p ~/nah-science
```

Load a finished run (for example the 5 keV calibration run) as real data. It is validated
first and only stored if it passes:

```bash
NAH_PG_DSN="dbname=nuclear" NAH_SCIENCE_DIR=~/nah-science python3 scripts/load_result.py <run_dir>
```

Start the site and open http://127.0.0.1:8080/ :

```bash
NAH_API_PG_DSN="dbname=nuclear" NAH_SCIENCE_DIR=~/nah-science python3 scripts/serve.py
```

## 2. Move it to a Raspberry Pi

Any Pi 4 or 5 with 2 GB or more and Raspberry Pi OS (64-bit) works for the website and database.
The BOINC server itself can join it later.

1. Install the packages on the Pi:
   ```bash
   sudo apt install git postgresql nginx gunicorn python3-psycopg python3-numpy python3-scipy python3-jsonschema
   ```
2. Copy the project and create its user:
   ```bash
   sudo git clone <your repo URL> /opt/nuclear-at-home   # or: rsync -a ~/Downloads/nuclear-at-home/ pi:/opt/nuclear-at-home/
   sudo useradd --system --home /opt/nuclear-at-home nah
   sudo mkdir -p /srv/nuclear/science && sudo chown nah /srv/nuclear/science
   ```
3. Create the database:
   ```bash
   sudo -u postgres createuser nah
   sudo -u postgres createdb -O nah nuclear
   sudo -u nah psql -d nuclear -f /opt/nuclear-at-home/stats/schema.sql
   ```
4. Copy your data from the laptop (database and result files):
   ```bash
   pg_dump nuclear | ssh pi 'sudo -u nah psql -d nuclear'
   rsync -a ~/nah-science/ pi:/tmp/nah-science/ && ssh pi 'sudo rsync -a /tmp/nah-science/ /srv/nuclear/science/ && sudo chown -R nah /srv/nuclear/science'
   ```
5. Start the API:
   ```bash
   sudo cp /opt/nuclear-at-home/server/nah-api.service /etc/systemd/system/
   sudo systemctl enable --now nah-api
   ```
6. Configure nginx:
   ```bash
   sudo cp /opt/nuclear-at-home/server/nginx_nah.conf /etc/nginx/sites-available/nuclear
   sudo ln -s /etc/nginx/sites-available/nuclear /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```
   - **Public domain:** set `server_name` and get a certificate with `sudo certbot --nginx`.
   - **Home network only:** in the 443 server block, replace `listen 443 ssl;` and `http2 on;` with
     `listen 80;`, delete the two `ssl_certificate` lines and the whole port-80 redirect block, and
     remove the `Strict-Transport-Security` line.
7. Open `http://<pi address>/`.

## Updating the site

Pages are plain files: `git pull` (or rsync) on the Pi is enough. API changes need
`sudo systemctl restart nah-api`. News posts are `viewer/news.json`.

## Security notes

- The API is read-only and has its own database role in production (`stats/schema.sql`).
- nginx rate-limits the API and sends a strict Content-Security-Policy. If you change the
  import map in `viewer/cascade.html`, recompute its hash in `server/nginx_nah.conf`.
- Never put the BOINC code-signing key on the Pi.
