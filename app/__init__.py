from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Set up the SQLAlchemy database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:roamiopass@172.28.237.236:5432/roamio'
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register routes
    from app.routes import init_app as init_routes
    init_routes(app)

    return app
