import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:roamiopass@localhost/roamio'
    SQLALCHEMY_TRACK_MODIFICATIONS = False