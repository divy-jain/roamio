from flask import request, url_for, render_template
from app import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    @app.context_processor
    def utility_processor():
        def url_for_other_page(page):
            args = request.args.copy()
            args['page'] = page
            return url_for(request.endpoint, **args)
        return dict(url_for_other_page=url_for_other_page)

    return app

def register_blueprints(app):
    from app.routes import auth, main, activity, itinerary, review
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(main.bp)
    app.register_blueprint(activity.bp, url_prefix='/activities')
    app.register_blueprint(itinerary.bp, url_prefix='/itineraries')
    app.register_blueprint(review.bp, url_prefix='/reviews')

# Error handlers
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

# Utility function to get an object or return a 404 error
def get_or_404(model, id):
    """Get a database object or return a 404 error using raw SQL."""
    result = db.session.execute(
        f'SELECT * FROM {model.__tablename__} WHERE id = :id', 
        {'id': id}
    ).fetchone()
    
    if result is None:
        return not_found_error(404)  # You may customize this to raise an error or handle differently

    return model(**result)
