from .user import User
from .activity import Activity
from .itinerary import Itinerary
from .review import Review

# You can add any model-related utility functions here if needed
def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def get_activities_by_city(city):
    return Activity.query.filter_by(city=city).all()

def get_user_itineraries(user_id):
    return Itinerary.query.filter_by(user_id=user_id).all()

def get_activity_reviews(activity_id):
    return Review.query.filter_by(activity_id=activity_id).all()

# You can also define any model-related constants here
ACTIVITY_TYPES = ['Sightseeing', 'Adventure', 'Cultural', 'Relaxation', 'Food & Drink']
SEASONS = ['Spring', 'Summer', 'Autumn', 'Winter', 'All Year']
COST_RANGES = ['$', '$$', '$$$', '$$$$']