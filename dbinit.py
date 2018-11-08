import os
import sys

import psycopg2 as dbapi2

DATABASE_URL = 'postgres://kbktqbcfmdxpbw:76006678dc4edef0501db56d75112cacde489dfb1be1648833f8ea853a1e32f4@ec2-54-247-101-191.eu-west-1.compute.amazonaws.com:5432/d1lo8nienmd3cn'

INIT_STATEMENTS = [
    """
        CREATE TABLE IF NOT EXISTS person
            (
                username character varying(20) PRIMARY KEY,
                fullname character varying(50) NOT NULL,
                emailaddress character varying(70) NOT NULL,
                userrole "char" NOT NULL,
                balance numeric(7,2) NOT NULL DEFAULT 0,
                CONSTRAINT person_fkey FOREIGN KEY (username)
                    REFERENCES users (username)
                    ON UPDATE RESTRICT
                    ON DELETE CASCADE
            )
    """,
    """
        CREATE TABLE IF NOT EXISTS users
            (
                username character varying(20) PRIMARY KEY,
                password character varying(50) NOT NULL
            )
    """,
    """
        CREATE TABLE IF NOT EXISTS posts
            (   postid SERIAL PRIMARY KEY,
                poster character varying(20) NOT NULL,
                content character varying(400) NOT NULL,
                date date,
                "time" time without time zone,
                CONSTRAINT posts_fkey FOREIGN KEY (poster)
                    REFERENCES users (username)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
            )
    """,
    """
        CREATE TABLE IF NOT EXISTS payments
            (   paymentid SERIAL PRIMARY KEY,
                username character varying(20) NOT NULL,
                amount numeric(7,2) NOT NULL,
                approved char NOT NULL DEFAULT '0',
                approved_by character varying(20),
                CONSTRAINT payments_fkey FOREIGN KEY (username)
                    REFERENCES users (username)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE,
                CONSTRAINT payments_fkey2 FOREIGN KEY (approved_by)
                    REFERENCES users (username)
                    ON UPDATE CASCADE
                    ON DELETE NO ACTION
            )
    """,
    """
            CREATE TABLE IF NOT EXISTS cities
                (   city_id integer PRIMARY KEY,
                    city character varying(20) NOT NULL
                )
    """,
    """
        CREATE TABLE IF NOT EXISTS planes
             (   plane_id integer PRIMARY KEY,
                plane_model character varying(30) NOT NULL,
                bsn_capacity integer,
                eco_capacity integer
            )
    """,
    """
        CREATE TABLE IF NOT EXISTS airports
             (   airport_id integer PRIMARY KEY,
                 airport_name character varying(100) NOT NULL,
                 city_id integer NOT NULL,
                 
                 CONSTRAINT airports_fkey FOREIGN KEY (city_id)
                    REFERENCES cities (city_id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT,
                
             )
    """,
    """
        CREATE TABLE IF NOT EXISTS flights
            (   flight_id integer PRIMARY KEY,
                destination_id  integer NOT NULL,
                departure_id integer NOT NULL,
                plane_id integer NOT NULL,
                departure_time timestamp without time zone,
                arrival_time timestamp without time zone,
               
                CONSTRAINT flights_fkey FOREIGN KEY (plane_id)
                    REFERENCES planes (plane_id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT,
                CONSTRAINT flights_fkey2 FOREIGN KEY (destination_id)
                    REFERENCES airports (airport_id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
                CONSTRAINT departure_fkey FOREIGN KEY (departure_id)
                    REFERENCES airports (airport_id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
            )
    """,
    """
        INSERT INTO users
        SELECT 'admin', 'admin' WHERE NOT EXISTS(select * from users where username='admin')
    """,
    """
        INSERT INTO person
        SELECT 'admin','Administrator', 'admin@airlinesss.com', 'A' WHERE NOT EXISTS(select * from person where username='admin')
    """,
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
