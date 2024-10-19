import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from werkzeug.security import generate_password_hash

# Database connection parameters
DB_NAME = "roamio"
DB_USER = "postgres"  # Default PostgreSQL superuser
DB_PASSWORD = "roamiopass"  # The password you set when creating the Docker container
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE {DB_NAME}")
    cur.close()
    conn.close()

def init_db():
    # Connect to the database
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()

    # Read schema.sql file
    with open('schema.sql', 'r') as f:
        schema = f.read()

    # Execute the SQL commands
    cur.execute(schema)

    # Insert sample data
    cur.execute("""
    INSERT INTO users (username, email, password_hash) VALUES
    ('john_doe', 'john@example.com', %s),
    ('jane_smith', 'jane@example.com', %s)
    """, (generate_password_hash('password123'), generate_password_hash('password456')))

    cur.execute("""
    INSERT INTO activities (name, description, city, activity_type, cost, season) VALUES
    ('Eiffel Tower Visit', 'Visit the iconic Eiffel Tower', 'Paris', 'Sightseeing', '$$', 'All Year'),
    ('Louvre Museum Tour', 'Explore world-famous artworks', 'Paris', 'Culture', '$$', 'All Year'),
    ('Tokyo Skytree', 'Visit the tallest tower in Japan', 'Tokyo', 'Sightseeing', '$$', 'All Year')
    """)

    # Commit the changes and close the connection
    conn.commit()
    cur.close()
    conn.close()

    print("Database initialized with sample data.")

if __name__ == "__main__":
    try:
        create_database()
    except psycopg2.errors.DuplicateDatabase:
        print(f"Database {DB_NAME} already exists.")
    init_db()