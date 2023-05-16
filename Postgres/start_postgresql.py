#!/usr/bin/env python3
import os
from create_tables import create_tables
import psycopg2 as psy

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def main():
    if not os.path.exists("data"):
        os.mkdir("data")

    os.system("initdb -D data/postgres")
    os.system("pg_ctl -D data/postgres -l logfile start")
    conn = psy.connect(dbname="postgres", user="jacobballard", password="postgres", host="localhost")
    # engine = create_engine(f"postgresql://jacobballard@localhost/postgres")
    # if not database_exists(engine.url):
    #     create_database(engine.url)
    # with engine.connect() as connection:
        # connection.execute("commit")
        # connection.autocommit = True
    
        # connection.execution_options(isolation_level="AUTOCOMMIT").execute(text("create database postgres;"))
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
    conn.commit()
    cur.execute(open('table_definitions.sql', 'r').read())
    # create_tables(conn)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()

