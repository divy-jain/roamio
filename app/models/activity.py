from app import db
from sqlalchemy import func
from app.models.review import Review
from app.models.itinerary import itinerary_activities  # Import the association table

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    cost = db.Column(db.String(10), nullable=False)
    season = db.Column(db.String(20), nullable=False)
    
    reviews = db.relationship('Review', back_populates='activity', lazy='dynamic')
    
    # Many-to-many relationship with Itinerary model using the itinerary_activities table
    itineraries = db.relationship('Itinerary', secondary=itinerary_activities, back_populates='activities')

    @property
    def average_rating(self):
        return db.session.query(func.avg(Review.rating)).filter(Review.activity_id == self.id).scalar() or 0.0

    def __repr__(self):
        return f'<Activity {self.name}>'
