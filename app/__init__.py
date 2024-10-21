from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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
    
    # Initialize Flask-Migrate with the app and db
    migrate = Migrate(app, db)

    # Import and register routes
    from app.routes import init_app as init_routes
    init_routes(app)

    return app
