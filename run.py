from app import create_app, db
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            logger.info("Starting Flask application")
        except Exception as e:
            logger.error(f"Error during startup: {e}")
            raise
            
    # Changed this line to disable reloader temporarily
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)


# from app import create_app, db
# import logging

# # Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(_name_)

# app = create_app()

# if _name_ == '_main_':
#     with app.app_context():
#         try:
#             # Note: We don't create tables here anymore since init_db.py handles that
#             logger.info("Starting Flask application")
#         except Exception as e:
#             logger.error(f"Error during startup: {e}")
#             raise
            
#     app.run(debug=True, host='0.0.0.0', port=5001)