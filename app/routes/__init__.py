from flask import request, url_for
from .auth import bp as auth_bp
from .activity import bp as activity_bp
from .itinerary import bp as itinerary_bp
from .review import bp as review_bp
from .main import bp as main_bp

def init_app(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(activity_bp, url_prefix='/activities')
    app.register_blueprint(itinerary_bp, url_prefix='/itineraries')
    app.register_blueprint(review_bp, url_prefix='/reviews')
    app.register_blueprint(main_bp)

    @app.context_processor
    def utility_processor():
        def url_for_other_page(page):
            args = request.args.copy()
            args['page'] = page
            return url_for(request.endpoint, **args)
        return dict(url_for_other_page=url_for_other_page)

# Constants
ITEMS_PER_PAGE = 20

# Error handlers
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

# You can add more utility functions here as needed
def get_or_404(model, id):
    """Get a database object or return a 404 error."""
    return model.query.get_or_404(id)