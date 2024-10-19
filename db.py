import psycopg2
from psycopg2 import pool

# Database connection parameters
DB_NAME = "roamio"
DB_USER = "postgres"
DB_PASSWORD = "roamiopass"
DB_HOST = "localhost"
DB_PORT = "5432"

# Create a connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

def get_db_connection():
    return connection_pool.getconn()

def release_db_connection(conn):
    connection_pool.putconn(conn)

def execute_query(query, params=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error executing query:", error)
        conn.rollback()
    finally:
        release_db_connection(conn)

def fetch_all(query, params=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data:", error)
    finally:
        release_db_connection(conn)

def fetch_one(query, params=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data:", error)
    finally:
        release_db_connection(conn)