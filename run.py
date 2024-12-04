import os
from app import create_app, db
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            logger.info("Starting Flask application")
        except Exception as e:
            logger.error(f"Error during startup: {e}")
            raise
    
    # Use the PORT environment variable for deployment; default to 5001 if not set
    port = int(os.environ.get('PORT', 5001))  # Default to 5001 if PORT is not set
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
