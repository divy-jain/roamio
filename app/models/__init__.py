from .user import User
from .activity import Activity
from .itinerary import Itinerary
from .review import Review

# Utility functions

def get_user_by_username(username):
    """Get a user by their username."""
    return User.query.filter_by(username=username).first()

def get_user_by_email(email):
    """Get a user by their email."""
    return User.query.filter_by(email=email).first()

def get_activities_by_city(city):
    """Get all activities for a specific city."""
    return Activity.query.filter_by(city=city).all()

def get_user_itineraries(user_id):
    """Get all itineraries for a specific user."""
    return Itinerary.query.filter_by(user_id=user_id).all()

def get_activity_reviews(activity_id):
    """Get all reviews for a specific activity."""
    return Review.query.filter_by(activity_id=activity_id).all()

def get_user_reviews(user_id):
    """Get all reviews by a specific user."""
    return Review.query.filter_by(user_id=user_id).all()

# Constants
ACTIVITY_TYPES = ['Sightseeing', 'Adventure', 'Cultural', 'Relaxation', 'Food & Drink']
SEASONS = ['Spring', 'Summer', 'Autumn', 'Winter', 'All Year']
COST_RANGES = ['$', '$$', '$$$', '$$$$']

# You can add more utility functions or constants as needed