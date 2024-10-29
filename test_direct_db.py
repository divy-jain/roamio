import psycopg2
import logging
from config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_direct_db_connection():
    try:
        # Parse the SQLAlchemy URL to get connection parameters
        url = Config.SQLALCHEMY_DATABASE_URI
        db_params = url.replace('postgresql://', '').split('@')
        user_pass = db_params[0].split(':')
        host_db = db_params[1].split('/')
        
        # Connect directly to PostgreSQL
        conn = psycopg2.connect(
            host=host_db[0],
            database=host_db[1],
            user=user_pass[0],
            password=user_pass[1],
            sslmode='require'
        )
        
        logger.info("Direct database connection successful!")
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Direct database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_direct_db_connection()