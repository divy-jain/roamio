from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Register blueprints here
    from app.routes import auth, main, activity, itinerary, review
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(activity.bp)
    app.register_blueprint(itinerary.bp)
    app.register_blueprint(review.bp)

    return app