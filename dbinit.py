import os
import sys

import psycopg2 as dbapi2

DATABASE_URL = 'postgres://kbktqbcfmdxpbw:76006678dc4edef0501db56d75112cacde489dfb1be1648833f8ea853a1e32f4@ec2-54-247-101-191.eu-west-1.compute.amazonaws.com:5432/d1lo8nienmd3cn'

INIT_STATEMENTS = [
    """
        CREATE TABLE IF NOT EXISTS person2
            (
                username character varying(20) NOT NULL,
                fullname character varying(50) NOT NULL,
                emailaddress character varying(70) NOT NULL,
                userrole "char" NOT NULL,
                balance numeric(7,2) NOT NULL DEFAULT 0,
                CONSTRAINT person_pkey2 PRIMARY KEY (username),
                CONSTRAINT username2 FOREIGN KEY (username)
                    REFERENCES users (username)
                    ON UPDATE RESTRICT
                    ON DELETE CASCADE
            )
    """,
    "CREATE TABLE IF NOT EXISTS DUMMY (NUM INTEGER)",
    "INSERT INTO DUMMY VALUES (42)",
]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
