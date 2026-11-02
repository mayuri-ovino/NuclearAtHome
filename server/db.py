"""Database connections. Credentials come from the environment, never from this repo.

NAH_PG_DSN       PostgreSQL DSN for the science/stats database (psycopg 3)
NAH_BOINC_MYCNF  MySQL option file with the BOINC MariaDB credentials (PyMySQL)
"""
import os


def pg():
    """Connection to the science database."""
    import psycopg  # dependency: psycopg[binary] >= 3.1 (server only)
    return psycopg.connect(os.environ["NAH_PG_DSN"])


def boinc():
    """Connection to BOINC's MariaDB (read-only use: host, user, team, result timing)."""
    import pymysql  # dependency: PyMySQL >= 1.1 (server only)
    return pymysql.connect(read_default_file=os.environ["NAH_BOINC_MYCNF"])
