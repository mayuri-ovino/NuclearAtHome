"""Database connections. Credentials come from the environment or from BOINC's own
config.xml at run time, never from this repo.

NAH_PG_DSN             PostgreSQL DSN for the science/stats database (psycopg 3)
NAH_BOINC_MYCNF        MySQL option file with the BOINC MariaDB credentials (PyMySQL), or
NAH_BOINC_PROJECT_DIR  the BOINC project directory: its config.xml holds the database login
                       (how BOINC's own tools connect; used inside the BOINC server container)
"""
import os
import xml.etree.ElementTree as ET
from pathlib import Path


def pg():
    """Connection to the science database."""
    import psycopg  # dependency: psycopg[binary] >= 3.1 (server only)
    return psycopg.connect(os.environ["NAH_PG_DSN"])


def boinc_login(config_xml: Path) -> dict:
    """host, user, password and database from a BOINC project's config.xml."""
    config = ET.parse(config_xml).getroot().find("config")
    field = lambda tag: (config.findtext(tag) or "").strip()
    return {"host": field("db_host") or "localhost", "user": field("db_user"),
            "password": field("db_passwd"), "database": field("db_name")}


def boinc():
    """Connection to BOINC's MariaDB (read-only use: host, user, team, result timing)."""
    import pymysql  # dependency: PyMySQL >= 1.1 (server only)
    if os.environ.get("NAH_BOINC_MYCNF"):
        return pymysql.connect(read_default_file=os.environ["NAH_BOINC_MYCNF"])
    return pymysql.connect(**boinc_login(Path(os.environ["NAH_BOINC_PROJECT_DIR"]) / "config.xml"))
