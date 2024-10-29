from app import create_app, db
from app.models import User

def test_db_connection():
    app = create_app()
    with app.app_context():
        try:
            # Try to query the database
            users = User.query.all()
            print("Database connection successful!")
            print(f"Found {len(users)} users in database")
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False

if __name__ == "__main__":
    test_db_connection()