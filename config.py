import os
from datetime import timedelta

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'

    #Changed here
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or (
    f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@"
    f"{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
)

    # # Database configuration - construct URI from individual parameters
    # SQLALCHEMY_DATABASE_URI = (
    #     f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@"
    #     f"{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
    # )
    
    # # Database configuration - use environment variable if available
    # SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
    #     'postgresql://postgres:roamiopass@db:5432/roamio'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Login configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Flask configuration
    DEBUG = True
    
    # Session configuration
    SESSION_COOKIE_SECURE = False  # Changed to False for development
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Application configuration
    ACTIVITIES_PER_PAGE = 10
    MAX_SEARCH_RESULTS = 50