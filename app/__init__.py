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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:roamiopass@roamio.czugw66qwqxb.us-east-2.rds.amazonaws.com:5432/roamio'
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import blueprints
    from app.routes import auth, main, activity, itinerary, review

    # Register routes
    init_app(app, auth.bp, main.bp, activity.bp, itinerary.bp, review.bp)

    return app

def init_app(app, auth_bp, main_bp, activity_bp, itinerary_bp, review_bp):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(activity_bp, url_prefix='/activities')
    app.register_blueprint(itinerary_bp, url_prefix='/itineraries')
    app.register_blueprint(review_bp, url_prefix='/reviews')
    app.register_blueprint(main_bp)

    # Register additional context processors or error handlers if needed
    @app.context_processor
    def utility_processor():
        from flask import request, url_for
        def url_for_other_page(page):
            args = request.args.copy()
            args['page'] = page
            return url_for(request.endpoint, **args)
        return dict(url_for_other_page=url_for_other_page)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

from app import models
