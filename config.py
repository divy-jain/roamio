import os
from datetime import timedelta

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Login configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Flask configuration
    DEBUG = False  # Changed to False for production
    
    # Session configuration
    SESSION_COOKIE_SECURE = True  # Changed to True for production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Application configuration
    ACTIVITIES_PER_PAGE = 10
    MAX_SEARCH_RESULTS = 50