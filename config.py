# File: /path/to/your/project/config.py
   # or
   # File: /path/to/your/project/config/config.py

import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:roamiopass@172.28.237.236:5432/roamio'
    SQLALCHEMY_TRACK_MODIFICATIONS = False