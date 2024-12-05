import psycopg2

# Replace these values with your RDS credentials
DATABASE_NAME = "roamio"
USERNAME = "postgres"
PASSWORD = "roamiopass"
HOST = "roamio.c1kos6auqw13.us-east-2.rds.amazonaws.com"
PORT = "5432"

try:
    # Attempt to connect to the RDS PostgreSQL instance
    connection = psycopg2.connect(
        database=DATABASE_NAME,
        user=USERNAME,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    print("✅ Database connection successful!")

    # Execute a simple query to verify
    cursor = connection.cursor()
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("📅 Current database time:", result)

except psycopg2.OperationalError as e:
    print("❌ Operational error while connecting to the database:", e)

except Exception as e:
    print("❌ Unexpected error:", e)

finally:
    # Ensure the connection is closed
    if 'connection' in locals() and connection:
        connection.close()
        print("🔒 Database connection closed.")
