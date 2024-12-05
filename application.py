from app import create_app, db
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the application instance - named 'application' for Elastic Beanstalk
application = create_app()

# Add a health check endpoint that EB will use
@application.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    with application.app_context():
        try:
            logger.info("Starting Flask application")
            db.create_all()  # Ensure database tables exist
        except Exception as e:
            logger.error(f"Error during startup: {e}")
            raise
            
    # Production configuration for Elastic Beanstalk
    application.run(
        host='0.0.0.0',
        port=5001,
        debug=False  # Disable debug mode in production
    )