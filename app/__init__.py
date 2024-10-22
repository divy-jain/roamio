from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Set up the SQLAlchemy database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:roamiopass@roamio.czugw66qwqxb.us-east-2.rds.amazonaws.com:5432/roamio'
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Import and register routes
    from app.routes import init_app as init_routes
    init_routes(app)

    return app
