from flask import Flask
from config import Config
import logging
from sqlalchemy import inspect, text
from app.routes.profile import profile_bp

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize extensions
from .extensions import db, login, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    
    # Configure login manager
    login.login_view = 'auth.login'
    login.login_message_category = 'info'

    # Import models AFTER db initialization
    from .models import User, Activity

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Register blueprints
    from .routes import auth, main, activity, itinerary, review
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(activity.bp)
    app.register_blueprint(itinerary.bp)
    app.register_blueprint(review.bp)
    app.register_blueprint(profile_bp)  # Register the profile blueprint


    # MODIFIED: Initialize database function
    def init_database():
        try:
            # First, check if tables already exist
            with db.engine.connect() as connection:
                exists_query = text("""
                    SELECT EXISTS (
                        SELECT 1 
                        FROM information_schema.tables 
                        WHERE table_name = 'users'
                    )
                """)
                tables_exist = connection.execute(exists_query).scalar()

            if not tables_exist:
                # Debug: Print the SQL for table creation
                logger.debug("Table creation SQL:")
                for table in db.metadata.tables.values():
                    logger.debug(str(table.compile(db.engine)))

                # Create all tables
                db.create_all()
                db.session.commit()
                logger.info("Database tables created successfully")

                # Debug: Check which tables actually exist
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()
                logger.debug(f"Existing tables after creation: {existing_tables}")

                # Print table schemas
                for table_name in existing_tables:
                    columns = inspector.get_columns(table_name)
                    logger.debug(f"Table {table_name} columns:")
                    for column in columns:
                        logger.debug(f"  {column['name']}: {column['type']}")

                # Add sample data
                logger.info("Adding sample data...")
                
                # Create dummy user
                dummy_user = User(
                    username='default_user', 
                    email='default@example.com',
                    profile_visibility=True  # Explicitly set profile_visibility
                )
                dummy_user.set_password('password123')
                db.session.add(dummy_user)
                db.session.commit()

                # Create sample activities
                activities = [
                    Activity(
                        name='Eiffel Tower Visit',
                        description='Visit the iconic Eiffel Tower',
                        city='Paris',
                        activity_type='Sightseeing',
                        cost='$$',
                        season='All Year', 
                        rating=5.0,
                        user_id=dummy_user.id
                    ),
                    Activity(
                        name='Louvre Museum Tour',
                        description='Explore world-famous artworks',
                        city='Paris',
                        activity_type='Culture',
                        cost='$$',
                        season='All Year', 
                        rating=5.0,
                        user_id=dummy_user.id
                    ),
                    Activity(
                        name='Tokyo Skytree',
                        description='Visit the tallest tower in Japan',
                        city='Tokyo',
                        activity_type='Sightseeing',
                        cost='$$',
                        season='All Year', 
                        rating=5.0,
                        user_id=dummy_user.id
                    )
                ]
                for activity in activities:
                    db.session.add(activity)

                db.session.commit()
                logger.info("Sample data added successfully")
            else:
                logger.info("Tables already exist, skipping initialization")
                
        except Exception as e:
            logger.error(f"Error during database initialization: {e}", exc_info=True)
            db.session.rollback()
            raise

    # Initialize database within context
    with app.app_context():
        init_database()

    return app


# from flask import Flask
# from config import Config
# import logging
# from sqlalchemy import inspect, text

# # Set up logging
# logging.basicConfig(
#     level=logging.DEBUG,  # Changed to DEBUG for more info
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# # Initialize extensions
# from .extensions import db, login, migrate

# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)
    
#     # Initialize extensions
#     db.init_app(app)
#     login.init_app(app)
#     migrate.init_app(app, db)
    
#     # Configure login manager
#     login.login_view = 'auth.login'
#     login.login_message_category = 'info'

#     # Import models AFTER db initialization
#     from .models import User, Activity  # Move this here

#     @login.user_loader
#     def load_user(id):
#         return User.query.get(int(id))

#     # Register blueprints
#     from .routes import auth, main, activity, itinerary, review
#     app.register_blueprint(auth.bp)
#     app.register_blueprint(main.bp)
#     app.register_blueprint(activity.bp)
#     app.register_blueprint(itinerary.bp)
#     app.register_blueprint(review.bp)

#     # Initialize database
#     def init_database():
#         try:
#             # Debug: Print the SQL for table creation
#             logger.debug("Table creation SQL:")
#             for table in db.metadata.tables.values():
#                 logger.debug(str(table.compile(db.engine)))

#             # Create all tables
#             db.create_all()
#             db.session.commit()
#             logger.info("Database tables created successfully")

#             # Debug: Check which tables actually exist
#             inspector = inspect(db.engine)
#             existing_tables = inspector.get_table_names()
#             logger.debug(f"Existing tables after creation: {existing_tables}")

#             # Print table schemas
#             for table_name in existing_tables:
#                 columns = inspector.get_columns(table_name)
#                 logger.debug(f"Table {table_name} columns:")
#                 for column in columns:
#                     logger.debug(f"  {column['name']}: {column['type']}")

#             # Add sample data only if there are no users
#             exists_query = text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users')")
#             result = db.session.execute(exists_query).scalar()
#             if not result:
#                 logger.error("Users table does not exist after creation!")
#                 return

#             count_query = text("SELECT COUNT(*) FROM users")
#             user_count = db.session.execute(count_query).scalar()
            
#             if user_count == 0:
#                 # Create sample users
#                 logger.info("Adding sample data...")
                
#                 # Create dummy user
#                 dummy_user = User(username='default_user', email='default@example.com')
#                 dummy_user.set_password('password123')
#                 db.session.add(dummy_user)
#                 db.session.commit()  # Commit to retrieve dummy_user.id

#                 # users = [
#                 #     User(username='john_doe', email='john@example.com'),
#                 #     User(username='jane_smith', email='jane@example.com')
#                 # ]
#                 # for user in users:
#                 #     user.set_password('password123')
#                 #     db.session.add(user)
#                 # db.session.commit()

#                 # Reload dummy_user in case of any changes during commit
#                 # dummy_user = User.query.filter_by(username='default_user').first()

#                 # Create sample activities
#                 activities = [
#                     Activity(
#                         name='Eiffel Tower Visit',
#                         description='Visit the iconic Eiffel Tower',
#                         city='Paris',
#                         activity_type='Sightseeing',
#                         cost='$$',
#                         season='All Year', 
#                         rating = 5.0,
#                         user_id=dummy_user.id  # Use specific user or dummy user
#                     ),
#                     Activity(
#                         name='Louvre Museum Tour',
#                         description='Explore world-famous artworks',
#                         city='Paris',
#                         activity_type='Culture',
#                         cost='$$',
#                         season='All Year', 
#                         rating = 5.0,
#                         user_id=dummy_user.id  # Use specific user or dummy user
#                     ),
#                     Activity(
#                         name='Tokyo Skytree',
#                         description='Visit the tallest tower in Japan',
#                         city='Tokyo',
#                         activity_type='Sightseeing',
#                         cost='$$',
#                         season='All Year', 
#                         rating = 5.0,
#                         user_id=dummy_user.id  # Use specific user or dummy user
#                     )
#                 ]
#                 for activity in activities:
#                     db.session.add(activity)

#                 db.session.commit()
#                 logger.info("Sample data added successfully")
#         except Exception as e:
#             logger.error(f"Error during database initialization: {e}", exc_info=True)
#             db.session.rollback()
#             raise

#     # Initialize database within context
#     with app.app_context():
#         init_database()

#     return app