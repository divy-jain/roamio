# __init__.py or app.py
from flask import Flask, redirect, url_for, request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from app.models import db, User
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Specify the login route

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  # Import here to avoid circular imports
        return User.query.get(int(user_id))

    # Import and register blueprints
    from .auth import auth as auth_blueprint
    from .main import main as main_blueprint
    from .activity import activity as activity_blueprint
    from .itinerary import itinerary as itinerary_blueprint
    from .review import review as review_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(activity_blueprint)
    app.register_blueprint(itinerary_blueprint)
    app.register_blueprint(review_blueprint)

    # Protect routes that require authentication
    @app.before_request
    def require_login():
        allowed_routes = ['auth.login', 'auth.register', 'main.index', 'static']
        if not current_user.is_authenticated and request.endpoint and request.endpoint not in allowed_routes:
            return redirect(url_for('auth.login'))

    return app

Copy@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))