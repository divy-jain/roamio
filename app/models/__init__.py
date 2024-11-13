from .user import User
from .activity import Activity
from .itinerary import Itinerary
from .review import Review
from ..extensions import db
from .user import User
from .friendship import FriendRequest, FriendshipStatus
from sqlalchemy.orm import joinedload

# Constants
ACTIVITY_TYPES = ['Sightseeing', 'Adventure', 'Cultural', 'Relaxation', 'Food & Drink']
SEASONS = ['Spring', 'Summer', 'Autumn', 'Winter', 'All Year']
COST_RANGES = ['$', '$$', '$$$', '$$$$']

# Utility functions
def get_user_by_username(username):
    """Get a user by their username."""
    return User.query.filter_by(username=username).first()

def get_user_by_email(email):
    """Get a user by their email."""
    return User.query.filter_by(email=email).first()

# def get_activities_by_city(city):
#     """Get all activities for a specific city."""
#     return Activity.query.filter_by(city=city).all()

# def get_user_itineraries(user_id):
#     """Get all itineraries for a specific user."""
#     return Itinerary.query.filter_by(user_id=user_id).all()

# def get_activity_reviews(activity_id):
#     """Get all reviews for a specific activity."""
#     return Review.query.filter_by(activity_id=activity_id).all()

# def get_user_reviews(user_id):
#     """Get all reviews by a specific user."""
#     return Review.query.filter_by(user_id=user_id).all()

def get_activities_by_city(city):
    """Get all activities for a specific city, including user details."""
    return Activity.query.options(joinedload('user')).filter_by(city=city).all()

def get_user_itineraries(user_id):
    """Get all itineraries for a specific user, including user details."""
    return Itinerary.query.options(joinedload('user')).filter_by(user_id=user_id).all()

def get_activity_reviews(activity_id):
    """Get all reviews for a specific activity, including user details."""
    return Review.query.options(joinedload('user')).filter_by(activity_id=activity_id).all()

def get_user_reviews(user_id):
    """Get all reviews by a specific user, including user details."""
    return Review.query.options(joinedload('user')).filter_by(user_id=user_id).all()

def create_indexes():
    """Create database indexes"""
    try:
        # Create Activity indexes
        db.Index('idx_activity_city', Activity.city)
        db.Index('idx_activity_type', Activity.activity_type)
        db.Index('idx_activity_season', Activity.season)
        
        # Create User indexes
        db.Index('idx_user_email', User.email)
        db.Index('idx_user_username', User.username)
        
        # Commit the index creation
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise